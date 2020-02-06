#! /usr/bin/env python3
#
# 2019-07-17
# Colton Grainger 

"""
Function definitions for the RDA images script (rdai).
"""

# messaging functions {{{
# These functions were originally part of MathBook XML.
# Adapted from https://github.com/rbeezer/mathbook/tree/dev/script
# Copyright 2010-2016 Robert A. Beezer, released GPLv2

def verbose(msg):
    """Write a message to the console on program progress"""
    try:
        global args
        # None if not set at all
        if args.verbose and args.verbose >= 1:
            print('utils.py: {}'.format(msg))
    except NameError:
        print('utils.py: {}'.format(msg))

def debug(msg):
    """Write a message to the console with some raw information"""
    try:
        global args
        # None if not set at all
        if args.verbose and args.verbose >= 2:
            print('utils.py: {}'.format(msg))
    except NameError:
        print('utils.py: {}'.format(msg))
# }}} 

# operating system functions {{{
# These functions were originally part of MathBook XML.
# Adapted from https://github.com/rbeezer/mathbook/tree/dev/script
# Copyright 2010-2016 Robert A. Beezer, released GPLv2

def get_rdai_path():
    """Returns path of root of RDAI distribution"""
    import sys, os.path
    verbose("discovering RDAI root directory from mbx script location")
    # full path to script itself
    rdai_path = os.path.abspath(sys.argv[0])
    # split "RDAI" executable off path
    script_dir, _ = os.path.split(rdai_path)
    # split "script" path off executable
    distribution_dir, _ = os.path.split(script_dir)
    verbose("RDAI distribution root directory: {}".format(distribution_dir))
    return distribution_dir


def get_source_path(source_file):
    """Returns path to content to be acted upon"""
    import sys, os.path
    verbose("discovering source directory from source location")
    # split path off filename
    source_dir, _ = os.path.split(source_file)
    return os.path.normpath(source_dir)

def get_executable(config, exec_name):
    "Queries configuration file for executable name, verifies existence in Unix"
    import os
    import platform
    import subprocess

    # http://stackoverflow.com/questions/11210104/check-if-a-program-exists-from-a-python-script
    # suggests  where.exe  as Windows equivalent (post Windows Server 2003)
    # which  = 'where.exe' if platform.system() == 'Windows' else 'which'

    # get the name, but then see if it really, really works
    debug('locating "{}" in [executables] section of configuration file'.format(exec_name))
    config_name = config.get('executables', exec_name)

    devnull = open(os.devnull, 'w')
    try:
        result_code = subprocess.call(['which', config_name], stdout=devnull, stderr=subprocess.STDOUT)
    except OSError:
        print('RDAI:WARNING: executable existence-checking was not performed (e.g. on Windows)')
        result_code = 0  # perhaps a lie on Windows
    if result_code != 0:
        error_message = '\n'.join([
                        'cannot locate executable with configuration name "{}" as command "{}"',
                        'Edit the configuration file and/or install the necessary program'])
        raise OSError(error_message.format(exec_name, config_name))
    debug("{} executable: {}".format(exec_name, config_name))
    return config_name

def get_cli_arguments():
    """Return the CLI arguments in parser object"""
    import argparse
    parser = argparse.ArgumentParser(description='RDAI utility script', formatter_class=argparse.RawTextHelpFormatter)

    verbose_help = '\n'.join(["verbosity of information on progress of the program",
                              "  -v  is actions being performed",
                              "  -vv is some additional raw debugging information"])
    parser.add_argument('-v', '--verbose', help=verbose_help, action="count")

    component_info = [
        ('metadata', 'Metadata for data files.'),
        ('uuid', 'UUIDs for data files.'),
        ('bundle', 'Bundle from metadata, UUIDs, and data files.'),
        ('database', 'Database from bundle.'),
    ]
    component_help = 'Possible components are:\n' + '\n'.join(['  {} - {}'.format(info[0], info[1]) for info in component_info])
    parser.add_argument('-c', '--component', help=component_help, action="store", dest="component")

    metadata_input_info = [
        ('csv', 'Recursively read *.csv files in data directory. Format: "key","value".'),
        ('json', 'Recursively read *.json files in data directory. Format: {"key":"value"}.'),
        ('xml', 'Read single *.xml file from root of data directory. See docs for XML Schema.'),
    ]
    metadata_input_help = 'Possible metadata input formats are:\n' + '\n'.join(['  {} - {}'.format(info[0], info[1]) for info in metadata_input_info])
    parser.add_argument('-m', '--metadata-input', help=metadata_input_help, action="store", dest='metadata_input')

    parser.add_argument('-d', '--data-dir', help='path to data directory', action="store", dest='data_dir')
    parser.add_argument('-o', '--output-dir', help='path to output directory', action="store", dest='output_dir')
    return parser.parse_args()

    # "nargs" allows multiple options following the flag
    # separate by spaces, can't use "-stringparam"
    # stringparams is a list of strings on return
    # parser.add_argument('-p', '--parameters', nargs='+', help='stringparam options to pass to XSLT extraction stylesheet (option/value pairs)',
    #                      action="store", dest='stringparams')
    # # default to an empty string, which signals root to XSL stylesheet
    # parser.add_argument('-r', '--restrict', help='restrict to subtree rooted at element with specified xml:id',
    #                      action="store", dest='xmlid', default='')
    # parser.add_argument('-s', '--server', help='base URL for server (webwork only)', action="store", dest='server')

def sanitize_directory(dir):
    """Verify directory name, or raise error"""
    # Use with os.path.join, and do not sweat separator
    import os.path
    verbose('verifying directory: {}'.format(dir))
    if not(os.path.isdir(dir)):
        raise ValueError('directory {} does not exist'.format(dir))
    return dir

# Certificate checking is buggy, exception raised is malformed
# 2015/10/07 Turned off verification in three places
# Command line warning can be disabled, requests.packages.urllib3.disable_warnings()
def sanitize_url(url):
    """Verify a server address, append a slash"""
    verbose('validating, cleaning server URL: {}'.format(url))
    import requests
    try:
        requests.get(url, verify=False)
    except requests.exceptions.RequestException as e:
        root_cause = str(e)
        msg = "There was a problem with the server URL, {}\n".format(url)
        raise ValueError(msg + root_cause)
    # We expect relative paths to locations on the server
    # So we add a slash if there is not one already
    if url[-1] != "/":
        url = url + "/"
    return url

def sanitize_alpha_num_underscore(param):
    """Verify parameter is a string containing only alphanumeric and undescores"""
    import string
    allowed = set(string.ascii_letters + string.digits + '_')
    verbose('verifying parameter: {}'.format(param))
    if not(set(param) <= allowed):
        raise ValueError('param {} contains characters other than a-zA-Z0-9_ '.format(param))
    return param

def get_config_info(script_dir, user_dir):
    """Return configuation in object for querying"""
    import sys,os.path
    config_filename = "rdai.cfg"
    default_config_file = os.path.join(script_dir, config_filename)
    user_config_file = os.path.join(user_dir, config_filename)
    config_file_list = [default_config_file, user_config_file]
    # ConfigParser was renamed to configparser in Python 3
    try:
        import configparser
    except ImportError:
        import ConfigParser as configparser
    config = configparser.SafeConfigParser()
    verbose("parsing configuration files: {}".format(config_file_list))
    files_read = config.read(config_file_list)
    debug("configuration files used/read: {}".format(files_read))
    if not(user_config_file in files_read):
        msg = "using default configuration only, custom configuration file not used at {}"
        verbose(msg.format(user_config_file))
    return config

def copy_data_directory(source_file, data_dir, tmp_dir):
    """Stage directory from CLI argument into the working directory"""
    import os.path, shutil
    verbose("formulating data directory location")
    source_full_path, _ = os.path.split(os.path.abspath(source_file))
    data_full_path = sanitize_directory(os.path.join(source_full_path, data_dir))
    data_last_step = os.path.basename(os.path.normpath(data_full_path))
    destination_root = os.path.join(tmp_dir, data_last_step)
    debug("copying data directory {} to working location {}".format(data_full_path, destination_root))
    shutil.copytree(data_full_path, destination_root)

def get_platform():
    """Return a string that tells us whether we are on Windows."""
    import platform
    return platform.system()

def is_os_64bit():
    """Return true if we are running a 64-bit OS.
    http://stackoverflow.com/questions/2208828/detect-64-bit-os-windows-in-python"""
    import platform
    return platform.machine().endswith('64')

def break_windows_path(python_style_dir):
    """Replace python os.sep with msys-acceptable "/" """
    import re
    return re.sub(r"\\", "/", python_style_dir)

# }}}

# uuid functions {{{

def get_fixed_seq():
    """Declares/updates global fixed_seq, which seeds mind_uuid()."""
    global fixed_seq
    from random import getrandbits
    fixed_seq = getrandbits(14)

def mint_uuid(node=None):
    """Returns a semi-sequential uuid. Requires global fixed_seq to have been
    defined as a seed."""
    import time
    from uuid import uuid1, getnode
    # answered 2019-05-16T13:46 by imposeren, CC-3.0
    # <https://stackoverflow.com/questions/56119272>

    # get_fixed_seq() should be called prior to mint_uuid().
    global fixed_seq

    # Returns a 32-character hexadecimal string, which can be
    # stored in MySQL as BINARY(16) for efficient indexing. C.f.,
    # <https://mysqlserverteam.com/storing-uuid-values-in-mysql-tables/>
    try:
        return uuid1(node=node, clock_seq=fixed_seq).hex
    except NameError:
        verbose("Failed to mint a uuid! Call 'get_fixed_seq()' before trying again.")

def get_exiftool():
    """Imports exiftool dependencies."""
    import subprocess
    repo_dir = subprocess.Popen(['git', 'rev-parse', '--show-toplevel'],
            stdout=subprocess.PIPE).communicate()[0].rstrip().decode('utf-8')
    import sys
    sys.path.append(os.path.join(repo_dir, "dependencies/pyexiftool"))
    import exiftool
    pass

def assign_uuid(filepath, overwrite=False):
    """Reads EXIF:ImageUniqueID tag for valid uuid. If no uuid exists, write mint_uuid() to EXIF:ImageUniqueID tag."""
    with exiftool.ExifTool() as et:
        uuid = et.get_tag('ImageUniqueID', filepath)

        # By default, if the `EXIF:ImageUniqueID` tag is empty, uuid is assigned to None.
        if (uuid is not None) and (overwrite is False):
            verbose("Tag EXIF:ImageUniqueID={} already exists in file {}.".format(uuid, filepath))

        # Else, no uuid was read by exiftool, or overwrite has been set to True.
        else:
            et.execute('-ImageUniqueID={}'.format(mint_uuid()).encode(), filepath.encode())
            os.remove(filepath+"_original")

            # Here, we only report back if the image file's uuid was updated.
            uuid = et.get_tag('ImageUniqueID', filepath)
            if uuid is not None:
                verbose("Wrote tag EXIF:ImageUniqueID={} to file {}.".format(uuid, filepath))
    return uuid
# }}}

# metadata functions {{{
# e.g., $ rdai -c metadata -m csv -d ~/data -o ~/tmp

# TODO def create_catalog(data_dir, output_dir, args.metadata_input):
# see 2019-11-21-minimal-working-example for an implementation

def pool_metadata(tagfile, normalized_catalog):
    """Collects key-value pairs from a given metadata tag file (here '.csv' or '.tsv'),
    then updates a given normalized catalog. TODO Add args for json or xml.

    :tagfile: Relative path to metadata file.
    :normalized_catalog: Dictionary to write out key-value pairs.
    :returns: Updated content dictionary.

    """
    import csv
    # Initial state.
    to_parse = False 

    # Test the well-formedness of key/value pairs in the tagfile.
    try:
        with open(tagfile, newline='') as file:

            # Read head of CSV file and determine dialect.
            try:
                dialect = csv.Sniffer().sniff(file.read(2048), delimiters=',\t')
                # If we can parse the header, then toggle to_parse and read the rest.
                to_parse = True
            except csv.Error as e:
                verbose('CSV Sniffer failed to parse file: {}, error: {}'.format(tagfile, e))

            if to_parse:
                file.seek(0)
                reader = csv.reader(file, dialect)
                # Read the tagfile (for the first two fields from each non-empty row).
                key_value_pairs = {
                        rows[0].strip():rows[1].strip()
                        for rows in reader if any(rows)}
                        # To concatenate all rows 2+, try. <ccg, 2019-07-27> 
                        # rows[0].strip():[x.strip for x in rows[1:]]
                # Add key_value_pairs to the current level of the
                # normalized_catalog dictionary.
                normalized_catalog = {
                        **normalized_catalog,
                        **key_value_pairs}

    # Message for key/value error.
    except csv.Error as e:
        verbose('Syntax error: key-value pair in file: {}, line {}: {}'.format(
            tagfile, reader.line_num, e))

    # Return normalized_catalog updated with key/value pairs from tagfile.
    return normalized_catalog

def get_normalized_catalog(data_dir, overwrite=False):
    """Catalogs the files and directories below the data_dir (relative path),
    given '.csv' or '.tsv' metadata (TODO or '.json') in the directory tree.

    :pool_metadata: "metadata gathering" function defined below.

    :data_dir: Relative path to directory to be cataloged. Should be a directory.
    :returns: Nested json describing files, directories, and metadata.

    """
    from pathlib import Path
    import os
    import magic
    import csv

    # Suppose data_dir is a parent.
    parent = Path(data_dir)

    # Initialize dictionary.
    normalized_catalog = {} 

    if parent.is_dir():
        # List relative paths to children.
        children = [os.path.join(parent, x) for x in sorted(os.listdir(parent))]
        # Recurse down by calling `get_normalized_catalog` for each child.
        normalized_catalog['contents'] = [get_normalized_catalog(child, overwrite=overwrite) 
                for child in children 
                if not os.path.basename(child).startswith(".")]
        # Note. We reserve the key 'contents' for inclusion of lists of child
        # dictionaries. The key 'contents' should appear 0 or 1 times in
        # each child dictionary.
        # TODO Add some type of "ignore" capabilities. For now, just ignore hidden files.  2019-11-21

        # Determine if `child` is a metadata tag file, and if so, in which input format.
        for child in children:
            _, ext = os.path.splitext(child)
            # TODO Test for xml and json.
            if ext in ['.csv', '.tsv']:
                # Update `normalized_catalog` with metadata from child.
                normalized_catalog = pool_metadata(child, normalized_catalog)

    # If the parent is not a directory, write out file-level metadata.
    # This is the floor of the recursive function call.
    else:
        normalized_catalog['file_path'] = str(parent)
        normalized_catalog['media_type'] = magic.from_file(str(parent), mime=True)
        # Eventually I'd like to restructure the program to recurse on
        # filetypes, so as to avoid reading headers redunandtly. At that
        # point, python-magic might not need to test for the file media_type. 2019-07-27
        if normalized_catalog['media_type'].startswith("image"):
            normalized_catalog['uuid'] = assign_uuid(str(parent), overwrite=overwrite)

    return normalized_catalog

# to unnormalize the json catalog in the output_dir ~/tmp
# TODO optimize recursive step <ccg, 2019-07-17> # 

def tail_flatten_list(flist,nlists):
    if nlists == []:
        return flist
    new_nlists = []
    new_flist = flist
    for nl in nlists:
        items = [i for i in nl if type(i) != list]
        lists = [l for l in nl if l not in items]
        new_flist.extend(items)
        new_nlists.extend(lists)
    return tail_flatten_list(new_flist, new_nlists)

def flatten_list(nl):
      items = [i for i in nl if type(i) != list]
      lists = [l for l in nl if l not in items]
      return tail_flatten_list(items, lists)

def tail_unnormalize_catalog(flatdict,lowerdicts):
    behead = lambda catalog: {k:v for k,v in catalog.items() if k != 'contents'}
    assimilate = lambda flatdict, catalog: \
        tail_unnormalize_catalog(
                {**flatdict, **behead(catalog)}, catalog['contents']) \
        if 'contents' in set(catalog.keys()) \
        else {**flatdict, **catalog}
    return [assimilate(flatdict, catalog) for catalog in lowerdicts]

def unnormalize_catalog(normalized_catalog):
    flatdict = {k:v for k,v in normalized_catalog.items() if k != 'contents'}
    lowerdicts = normalized_catalog['contents']
    catalog = flatten_list(tail_unnormalize_catalog(flatdict, lowerdicts))
    return catalog

def write_timestamped_catalog(catalog, output_dir):
    import json 
    import os
    import datetime
    ts = str(datetime.datetime.now().strftime("%Y-%m-%d-%H%M%S"))
    with open(os.path.join(output_dir, '{}-catalog.json'.format(ts)), 'w') as fp:
        json.dump(catalog, fp, indent=4)

# }}}

# bundle functions {{{

def read_timestamped_catalog(output_dir):
    import json
    import os
    import glob
    try:
        most_recent_catalog = [c for c in 
                sorted(glob.glob(os.path.join(output_dir,'*-catalog.json')))][-1]
        with open(most_recent_catalog, 'r') as fp:
            catalog = json.load(fp)
        return catalog
    except IndexError: 
        verbose("The directory {} does not contain a JSON catalog ending in '*-catalog.json'.".format(output_dir))

# TODO add configuration for "remote" output_dir <ccg, 2019-07-17> # 
# def rename_by_uuids(data_dir, output_dir):

# }}}

# database functions {{{

# image = Table('image', metadata,
#     Column('image_id', String(36), pimary_key=True),
#     Column('document_id', ForeignKey('document.document_id')),
#     Column('relative_order', Integer(4), nullable=False)
# e.g., $ rdai -c database -o ~/tmp
# to retrieve the database config and handle errors
# to initialize a test database with the rdai schema
# to inject bundled metadata into the test database
# 2019-06-25-create-sql-engine.py

# }}}

# NARA functions {{{ # 
# 2019-06-01-sample-downloads.py
#  }}} 
