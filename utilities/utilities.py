#!/usr/bin/env python

#############################################################
#
# Retain from original utilities, only file IO, URL processing, and logging methods
# Add timing calls
# That can be used by any of the ADCIRC support tools
#
# Rebuilt logging mewthod baseed in part on the work of P. Owen's Supervisor code
#
# RENCI 2020
#############################################################

import sys,os
import yaml
import logging
import json

LOGGER = None

class utilities:
    """
    Class to manage the logging setup.

    """
    @staticmethod
    def init_logging(subdir=None, config_file=None):
        """
        Initialize the Utilities class, set up logging
        """
        global LOGGER
        config_data = utilities.load_config(yaml_file=config_file)
        if LOGGER is None:
            log = utilities.initialize_logging(subdir=subdir, config=config_data)
            LOGGER = log
        utilities.log = LOGGER
        return config_data

    def initialize_logging(subdir=None, config=None):
        """
        Log file get saved to $LOG_PATH/subdir. LOG_PATH defaults to '.'

        Parameters
            config: dictionary containing logging settings (usually this is main.yml)
            subdir: A subdirectory constructed beneath the value in LOG_PATH 
        Returns
            logger handle
        """
        # logger = logging.getLogger(__name__)
        logger = logging.getLogger("ast_services") # We could simply add the instanceid here as well

        log_level = config["DEFAULT"].get('LOGLEVEL', 'DEBUG')
        logger.setLevel(log_level)

        if subdir is not None:
            Logdir = '/'.join([os.getenv('LOG_PATH','.'),subdir])
        else:
            Logdir = os.getenv('LOG_PATH','.')

        #LogName =os.getenv('LOG_NAME','logs')
        LogName='AdcircSupportTools.log'
        LogFile='/'.join([Logdir,LogName])
        self.LogFile = LogFile

        formatter = logging.Formatter('%(asctime)s : %(levelname)s : %(funcName)s : %(module)s : %(name)s : %(message)s ')
        dirname = os.path.dirname(LogFile)
        if dirname and not os.path.exists(dirname):
            os.makedirs(dirname)
        file_handler = logging.FileHandler(LogFile, mode='w')
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        return logger
# YAML
    def load_config(yaml_file=None):
        if yaml_file is None:
            utilities.log.error('Called load_config but didnt specify yaml name: ABORT')
            sys.exit(1)
        if not os.path.exists(yaml_file):
            raise IOError("Failed to load yaml config file {}".format(yaml_file))
        with open(yaml_file, 'r') as stream:
            config = yaml.safe_load(stream)
            print('Opened yaml file {}'.format(yaml_file,))
        return config


