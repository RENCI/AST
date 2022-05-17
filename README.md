# AST
AST: AdcircSupportTools 

AST is a suite of classes and methods to facilitate the acquisition of observation and model time series data in support of work in ADCIRC Data Analysis (ADDA), Visualization of Hurricane tracks (APSVIZ2), and 41-year reanalysis.

AST provides to user applications, a common entry point to a variety of measured and modelled data sources currently including NOAA/NOS, Contrails (OneRain), NDBC, and ASGS. AST is an extensible design permitting easy addition of new sources overtime.
AST provides time series data products (currently only water_level, air_pressure, wind_speed) from all defined sources in a harmonized and consistent format and with aligned time steps.

This repo consists of two groups of code: harvester and processing.
    harvester abstracts the acquisition of data_product time series from multiple data sources. Test examples may be found in ./harvester/documents/README.
    processing includes the computation of residual pairs and interpolation onto user supplied grids


