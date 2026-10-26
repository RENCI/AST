import os
import sys
import types
import unittest
from pathlib import Path
from unittest import mock

import numpy as np
import numpy.ma as ma
import pandas as pd


AST_ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0, str(AST_ROOT))


def _install_import_stubs():
    sys.modules.setdefault('xarray', types.ModuleType('xarray'))
    sys.modules.setdefault('noaa_coops', types.ModuleType('noaa_coops'))
    sys.modules.setdefault('buoypy', types.ModuleType('buoypy'))
    sys.modules.setdefault('netCDF4', types.ModuleType('netCDF4'))

    siphon=types.ModuleType('siphon')
    simplewebservice=types.ModuleType('siphon.simplewebservice')
    ndbc=types.ModuleType('siphon.simplewebservice.ndbc')
    ndbc.NDBC=object
    catalog=types.ModuleType('siphon.catalog')
    catalog.TDSCatalog=object
    sys.modules.setdefault('siphon', siphon)
    sys.modules.setdefault('siphon.simplewebservice', simplewebservice)
    sys.modules.setdefault('siphon.simplewebservice.ndbc', ndbc)
    sys.modules.setdefault('siphon.catalog', catalog)

    dataretrieval=types.ModuleType('dataretrieval')
    nwis=types.ModuleType('dataretrieval.nwis')
    dataretrieval.nwis=nwis
    sys.modules.setdefault('dataretrieval', dataretrieval)
    sys.modules.setdefault('dataretrieval.nwis', nwis)


_install_import_stubs()

from harvester.fetch_station_data import adcirc_fetch_data, fetch_station_data
from utilities.utilities import utilities
import harvester.fetch_station_data as fetch_station_data_module


class _TimeVariable:
    units='seconds since 2026-10-21 00:00:00'

    def __init__(self, size):
        self.size=size

    def __getitem__(self, key):
        return np.arange(self.size)


class _DataVariable:
    dimensions=('time', 'station')

    def __init__(self, values, fail):
        self.values=values
        self.fail=fail

    def __getitem__(self, key):
        if self.fail:
            raise OSError('transient DAP read failure')
        return self.values


class _Dataset:
    source='fixture'

    def __init__(self, factory, fail):
        self.factory=factory
        self.variables={
            'time': _TimeVariable(len(factory.values)),
            'zeta': _DataVariable(factory.values, fail),
        }

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, traceback):
        self.factory.closes += 1

    def __getitem__(self, key):
        return self.variables[key]


class _DatasetFactory:
    def __init__(self, failures, values=None):
        self.failures=failures
        self.values=values if values is not None else ma.array([1.0, 2.0, 3.0])
        self.opens=0
        self.closes=0

    def __call__(self, url):
        self.opens += 1
        return _Dataset(self, self.opens <= self.failures)


class _OpenFailureFactory(_DatasetFactory):
    def __call__(self, url):
        self.opens += 1
        if self.opens <= self.failures:
            raise OSError('transient dataset open failure')
        return _Dataset(self, False)


def _adapter():
    adapter=object.__new__(adcirc_fetch_data)
    adapter._variable_name='zeta'
    return adapter


class AdcircRetryTests(unittest.TestCase):
    def setUp(self):
        utilities.log=mock.Mock()
        self.env=mock.patch.dict(
            os.environ,
            {
                'AST_IO_RETRY_ATTEMPTS': '3',
                'AST_IO_RETRY_PAUSE': '0',
                'AST_IO_RETRY_MAX_PAUSE': '0',
            },
        )
        self.env.start()
        self.addCleanup(self.env.stop)

    def test_transient_read_recovers_ctin7_and_closes_each_dataset(self):
        values=ma.array([1.0, -99999.0, 3.0], mask=[False, True, False])
        factory=_DatasetFactory(failures=1, values=values)
        with mock.patch.object(fetch_station_data_module.nc4, 'Dataset', factory, create=True), \
             mock.patch.object(
                 fetch_station_data_module.nc4,
                 'num2date',
                 return_value=pd.date_range('2026-10-21', periods=3, freq='h'),
                 create=True,
             ), \
             mock.patch.object(fetch_station_data_module.time, 'sleep') as sleep:
            result=_adapter().fetch_single_product(('CTIN7', 75), ['fixture.nc'])

        self.assertEqual(['CTIN7'], result.columns.tolist())
        self.assertEqual(2, factory.opens)
        self.assertEqual(2, factory.closes)
        sleep.assert_not_called()
        log_text=' '.join(call.args[0] for call in utilities.log.info.call_args_list)
        self.assertIn('station=CTIN7', log_text)
        self.assertIn('total=3', log_text)
        self.assertIn('finite=2', log_text)
        self.assertIn('masked=1', log_text)
        self.assertIn('missing=1', log_text)

    def test_exhausted_retries_raise_station_specific_error_and_close(self):
        factory=_DatasetFactory(failures=3)
        with mock.patch.object(fetch_station_data_module.nc4, 'Dataset', factory, create=True), \
             mock.patch.object(
                 fetch_station_data_module.nc4,
                 'num2date',
                 return_value=pd.date_range('2026-10-21', periods=3, freq='h'),
                 create=True,
             ):
            with self.assertRaisesRegex(RuntimeError, 'CTIN7 produced no data after retries'):
                _adapter().fetch_single_product(('CTIN7', 75), ['fixture.nc'])

        self.assertEqual(3, factory.opens)
        self.assertEqual(3, factory.closes)

    def test_dataset_open_is_part_of_retry_operation(self):
        factory=_OpenFailureFactory(failures=1)
        with mock.patch.object(fetch_station_data_module.nc4, 'Dataset', factory, create=True), \
             mock.patch.object(
                 fetch_station_data_module.nc4,
                 'num2date',
                 return_value=pd.date_range('2026-10-21', periods=3, freq='h'),
                 create=True,
             ):
            result=_adapter().fetch_single_product(('CTIN7', 75), ['fixture.nc'])

        self.assertEqual(['CTIN7'], result.columns.tolist())
        self.assertEqual(2, factory.opens)
        self.assertEqual(1, factory.closes)

    def test_aggregate_records_explicit_exclusion_reason(self):
        class FixtureAdapter(fetch_station_data):
            def fetch_single_product(self, station, periods):
                if station == 'CTIN7':
                    raise RuntimeError('exhausted retries')
                return pd.DataFrame(
                    {station: [1.0]},
                    index=pd.DatetimeIndex(['2026-10-21'], name='TIME'),
                )

        adapter=FixtureAdapter(['CONTROL', 'CTIN7'], [], resample_mins=0)
        result=adapter.aggregate_station_data(perform_interpolation=False)

        self.assertEqual(['CONTROL'], result.columns.tolist())
        self.assertIn('CTIN7', adapter.data_exclusions)
        self.assertIn('exhausted retries', adapter.data_exclusions['CTIN7'])


if __name__ == '__main__':
    unittest.main()
