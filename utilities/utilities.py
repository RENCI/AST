#!/usr/bin/env python

#############################################################
#
# Retain from original utilities, only file IO, URL processing, and logging methods
# Add timing calls
# That can be used by any of the ADCIRC support tools
#
# RENCI 2020
#############################################################

import sys,os
import yaml
import logging
import json

LOGGER = None

class Utilities:
    """

    """
    def __init__(self, instanceid=None):
        """
        Initialize the Utilities class, set up logging
        """
        global LOGGER
        self.config = self.load_config()

        if LOGGER is None and self.config["DEFAULT"]["LOGGING"]:
            log = self.initialize_logging(instanceid)
            LOGGER = log
        self.log = LOGGER

#############################################################
# Logging

    def initialize_logging(self, instanceid=None):
        """
        Initialize project logging
        instanceid is a subdirectory to be created under LOG_PATH
        """
        # logger = logging.getLogger(__name__)
        logger = logging.getLogger("adda_services") # We could simply add the instanceid here as well
        log_level = self.config["DEFAULT"].get('LOGLEVEL', 'DEBUG')
        # log_level = getattr(logging, self.config["DEFAULT"].get('LOGLEVEL', 'DEBUG'))
        logger.setLevel(log_level)

        # LogFile = self.config['LOG_FILE']
        # LogFile = '{}.{}.log'.format(thisDomain, currentdatecycle.cdc)
        #LogFile = 'log'
        #LogFile = os.getenv('LOG_PATH', os.path.join(os.path.dirname(__file__), 'logs'))
        if instanceid is not None:
            Logdir = '/'.join([os.getenv('LOG_PATH','.'),instanceid])
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

#############################################################
# YAML
    def load_config(self, yaml_file=os.path.join(os.path.dirname(__file__), '../config', 'main.yml')):
        if yaml_file is None:
            utilities.log.error('Called load_config but didnt specify yaml name: ABORT')
            sys.exit(1)
        if not os.path.exists(yaml_file):
            raise IOError("Failed to load yaml config file {}".format(yaml_file))
        with open(yaml_file, 'r') as stream:
            config = yaml.safe_load(stream)
            print('Opened yaml file {}'.format(yaml_file,))
        return config

    def read_config_yml(self, yamlfilename):
        if not os.path.exists(yamlfilename):
            raise IOError("Failed to find config file %s" % yamlfilename)
        # config_file = EnvYAML(yamlfilename)
        # print(config_file['ADDAHOME'])
        with open(yamlfilename, 'r') as stream:
            config_file = yaml.safe_load(stream)
        return config_file

utilities = Utilities()

