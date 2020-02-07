#! /usr/bin/env python3
#
# 2019-06-25 
# Colton Grainger 
# CC-0 Public Domain

import subprocess
import configparser
import os
from sqlalchemy import create_engine

def git_repo_abs_dir():
    return subprocess.check_output(
            ['git', 'rev-parse', '--show-toplevel']).decode().rstrip()

def create_images_db_engine(defaults_extra_file):
    """Connects to the `images` database with sqlalchemy, given a 
    configuration file for the mysql client.

    :defaults_extra_file: A string that is the relative path to the
    configuration file specified by the --defaults-extra-file in the
    rda-image-archive repository's Makefile. Is relative to the root of the git
    repo.
    :returns: A sqlalchemy.engine.base.Engine object for use with pandas.

    """
    dbconfig = configparser.ConfigParser()
    dbconfig.read(os.path.join(git_repo_abs_dir(), defaults_extra_file))
    mysql_args = dict(dbconfig['client'])

    return create_engine("mysql+pymysql://{user}:{password}@{host}/images"
                           .format(**mysql_args))
