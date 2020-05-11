#! /usr/bin/env python3
#
# 2020-05-03 
# Colton Grainger 
# CC-0 Public Domain

""" 
Configuration for

1. a SQLAlchemy database url and session
2. the Ingest, Data, and Output Directory classes and methods
"""

import os
import configparser
import exiftool
import shutil
import tarfile
import re
import pandas as pd

from pprint import pprint
from datetime import datetime
from distutils.dir_util import copy_tree
from os.path import expandvars
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from imagearchive.schema import Base, Archive, Platform, Document, Image
from imagearchive.utils import get_fixed_seq
from imagearchive.utils import get_normalized_catalog
from imagearchive.utils import unnormalize_catalog
from imagearchive.utils import write_timestamped_catalog
from imagearchive.utils import read_timestamped_catalog

# absolute path for ./default_config.ini
default_config = os.path.abspath(os.path.join(os.path.dirname(__file__), 'default_config.ini'))

def configure(config_file=default_config):
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

def setup_database_engine(config_file=default_config):
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

def setup_directories(config_file=default_config):
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

class Directory:

    """Abstraction for file operations in a directory"""

    def __init__(self, *, abspath, **kwargs):
        """Initializes the Directory, creating one if it doesn't exist.

        :abspath: str, absolute path to directory

        """
        self.abspath = expandvars(abspath)
        Path(self.abspath).mkdir(parents=True, exist_ok=True)

    def __repr__(self):
        return f"Directory(abspath='{self.abspath}')"

    @staticmethod
    def remove_content(absolute_path):
        try:
            for filename in os.listdir(absolute_path):
                file_path = os.path.join(absolute_path, filename)
                try:
                    if os.path.isfile(file_path) or os.path.islink(file_path):
                        os.unlink(file_path)
                    elif os.path.isdir(file_path):
                        shutil.rmtree(file_path)
                except Exception as e:
                    print(f'Failed to delete {file_path}. Reason: {e}')
        except NotADirectoryError as e:
            os.unlink(absolute_path)

    def empty_some(self, content=[]):
        """
        Empties specified content from the Directory.

        :content: Defaults to an empty list, in which case nothing in the
        Directory is removed. If 'content' is an iterator of relative paths to the
        Directory's root, these paths only are removed.
        """
        try:
            for relative_path in content:
                self.remove_content(os.path.join(self.abspath, relative_path))
        except TypeError:
            raise ValueError(f'Argument {content} is not iterable')

    def empty_all(self):
        """Empties all content from the Directory."""
        print(f'Removing all content under {self.abspath} ...')
        self.remove_content(self.abspath)

    def fetch_all_from(self, src_directory):
        """
        Copies all content from 'src_directory' instance to the Directory.
        This is a wrapper method for distutils.dir_util.copy_tree

        :src_directory: Directory instance to copy content from

        """
        copy_tree(src_directory.abspath, self.abspath)

    def fetch_some_from(self, src_directory, content=[]):
        """
        Copies specified content from 'src_directory' instance to the Directory.

        :src_directory: Directory instance to copy content from
        :content: Defaults to an empty list, in which case nothing happens. 
        If 'content' is an iterator of relative paths from the src_directory's
        root, these paths only are copied.
        """
        try:
            for relative_path in content:
                shutil.copy(os.path.join(src_directory.abspath, relative_path),
                        self.abspath)
        except TypeError:
            raise ValueError(f'Argument {content} is not iterable')

    def create_tar_archive(self, outdir=None):
        """Creates a gzipped tar archive of the Directory's contents, in the
        Directory itself, unless 'outdir' is specified. I recommend leaving
        outdir as None. In good OO-design, objects should be responsible for
        mutating themselves.

        :outdir: (optional) a Directory instance, not recommended
        :returns: path to gzipped tar archive

        """
        # for the tar archive filename, we need a timestamp 
        timestamp = datetime.now().strftime('%F-%H%M%S') # e.g., '2020-04-21-132052'
        directory_basename = os.path.basename(self.abspath)
        tar_archive_name = f"{timestamp}-{directory_basename}.tar.gz"
        try:
            tar_archive_abspath = os.path.join(outdir.abspath, tar_archive_name)
        except AttributeError:
            tar_archive_abspath = os.path.join(self.abspath, tar_archive_name)
        with tarfile.open(tar_archive_abspath, mode="w:gz") as tar:
            print(f"Creating tar archive {tar_archive_abspath} ...")
            tar.add(self.abspath, arcname=f"{timestamp}-{directory_basename}")
        return tar_archive_abspath

    def remove_tar_archive(self):
        """
        Removes any gzipped tar archives contained in the Directory, if they exist.
        """
        for item in os.listdir(self.abspath):
            if item.endswith(".tar.gz"):
                tar_archive_abspath = os.path.join(self.abspath, item)
                print(f"Removing tar archive {tar_archive_abspath} ...")
                os.remove(tar_archive_abspath)
        
    @classmethod
    def from_relpath(cls, relative_path):
        """Initializes the Directory from a relative path."""
        return cls(abspath=os.path.abspath(relative_path))

class IngestDirectory(Directory):

    """Images are to be ingest from an IngestDirectory"""

    def __init__(self, **kwargs):
        get_fixed_seq()
        super().__init__(**kwargs)

    def catalog(self, overwrite=False, debug=False):
        """Parses its contents and writes an unnormalized catalog at its root.

        :overwrite: Boolean option to overwrite the EXIF tag ImageUniqueID of
        all image files contained in the IngestDirectory (helpful when ingesting
        documents for the first time to ensure that this tag is written with an
        imagearchive uuid rather than containing an ImageUniqueID from, e.g.,
        the smartphone that created the image).
        :debug: Boolean option to pretty print the unnormalized catalog created
        during this method's call.
        :returns: a list containing, for each file in the IngestDirectory, a 
        dictionary containing key-value pairs corresponding to metadata fields
        and specific metadata entries.

        """
        normalized_catalog = get_normalized_catalog(self.abspath,
                overwrite=overwrite)
        if debug:
            pprint(normalized_catalog)
        catalog = unnormalize_catalog(normalized_catalog)
        write_timestamped_catalog(catalog, self.abspath)
        return catalog

class DataDirectory(Directory):

    """Abstraction for directory and database containing successfully ingested
    images"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def open_session(self, engine):
        """
        Associates a SQLAlchemy Session() object to the DataDirectory.session
        attribute, given a database engine.
        """
        Base.metadata.create_all(engine)
        Session = sessionmaker(bind=engine)
        self.session = Session()

    def close_session(self):
        """
        Wrapper for DataDirectory.session.close().
        """
        self.session.close()

    def inspect_and_prepare(self, catalog):
        df = pd.DataFrame(catalog)
        df = df[df['media_type'].str.contains("image")]
        arc_df = df.filter(regex=("^archive")).drop_duplicates()
        arc_df.rename(columns=lambda x: re.sub('archive.','',x), inplace=True)
        arc_catalog = arc_df.to_dict('records')
        for arc_metadata in arc_catalog:
            try:
                archive = Archive(**arc_metadata)
                self.session.add(archive)
                self.session.flush()
            except IntegrityError:
                archive = self.session.query(Archive).filter(
                        Archive.country_code = arc_metadata['country_code'], 
                        Archive.name = arc_metadata['name']).one()
            arc_metadata['Archive'] = archive
        return arc_catalog

class OutputDirectory(Directory):

    """Images are to be output to an OutputDirectory"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
