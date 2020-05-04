#! /usr/bin/env python3
#
# 2020-05-03 
# Colton Grainger 
# CC-0 Public Domain

"""
Configuration structure
"""

import configparser

from sqlalchemy import create_engine

from .directories import IngestDirectory, DataDirectory, OutputDirectory

def configure(config_file='../docs/default_config.ini'):
    """
    Reads a configuration (INI format) file that specifies the three working
    directories for binary image files, as well as the preferred database
    connection.

    A configuration file should contain two sections: 

    1. A [directories] section that gives absolute paths to three directories:
    ingest_dir, an ingest directory, where one will ingest images from;
    data_dir, a data directory, where one will keep ingested binary image files;
    output_dir, an output directory, where one will ouput tarfiles to images.

    2. A [database] section that gives info to create a SQLAlchemy database URL.

    :config_file: path to configuration file
    :returns: configparser.ConfigParser() instance

    """

    configuration = configparser.ConfigParser()
    configuration.read(config_file)
    return configuration

def setup_database_engine(config_file='../docs/default_config.ini'):
    """
    Wrapper around sqlalchemy.create_engine() that obtains a database URL
    from the specified config_file.

    :config_file: path to configuration file
    :returns: sqlalchemy.Engine() instance

    """

    conf = configure(config_file)
    if conf['database'].getboolean('sqlite'):
        engine = create_engine('sqlite:///:memory:')
    else:
        params = conf['database']
        engine = create_engine(
                    f'{params["dialect"]}'
                    + f'+{params["driver"]}'
                    + f'://{params["username"]}'
                    + f':{params["password"]}'
                    + f'@{params["host"]}'
                    + (f':{params["port"]}/' if params["port"] else '/')
                    + f'{params["database"]}'
                    )
    return engine

##

def setup_directories(config_file='../docs/default_config.ini'):
    """
    Creates three working directories at paths specified in config_file (if they
    fail to exit) for binary image files by instanstiating three corresponding
    Directory objects.

    :config_file: path to configuration file
    :returns: tuple(IngestDirectory(), DataDirectory(), OutputDirectory())
    
    """
    params = configure(config_file)['directories']
    return (IngestDirectory(abspath=params['ingest_dir']),
            DataDirectory(abspath=params['data_dir']),
            OutputDirectory(abspath=params['output_dir']))
