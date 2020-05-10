#! /usr/bin/env python3
#
# 2019-07-17
# Colton Grainger 
# CC-0 Public Domain

"""
Utility functions for methods on the Directory classes, esp. for the image
ingestion workflow. Defines `get_normalized_catalog`, which implicitly
assumes that CSV or TSV metadata "tagfiles" are embedded in the directory tree
containing images to be ingest.
"""

import sys
import os
sys.path.insert(1, os.path.abspath(
    os.path.join(os.path.dirname(__file__), '../dependencies/pyexiftool')))
import exiftool
import json 
import glob
import magic
import csv

from datetime import datetime
from random import getrandbits
from uuid import uuid1, getnode
from pathlib import Path

def get_fixed_seq():
    """Declares/updates global fixed_seq, which seeds mind_uuid()."""
    global fixed_seq
    fixed_seq = getrandbits(14)

def mint_uuid(node=None):
    """Returns a semi-sequential uuid. Requires global fixed_seq to have been
    defined as a seed."""
    # answered 2019-05-16T13:46 by imposeren, CC-3.0
    # <https://stackoverflow.com/questions/56119272>

    # get_fixed_seq() should be called prior to mint_uuid().
    global fixed_seq

    # Returns a 32-character hexadecimal string, which could be
    # stored in MySQL as BINARY(16) for efficient indexing. C.f.,
    # <https://mysqlserverteam.com/storing-uuid-values-in-mysql-tables/>
    try:
        return uuid1(node=node, clock_seq=fixed_seq).hex
    except NameError:
        print("Failed to mint a uuid! Call 'get_fixed_seq()' before trying again.")

def assign_uuid(filepath, overwrite=False):
    """Reads EXIF:ImageUniqueID tag for valid uuid. If no uuid exists, write mint_uuid() to EXIF:ImageUniqueID tag."""
    with exiftool.ExifTool() as et:
        uuid = et.get_tag('ImageUniqueID', filepath)

        # By default, if the `EXIF:ImageUniqueID` tag is empty, uuid is assigned to None.
        if (uuid is not None) and (overwrite is False):
            print(f"Tag EXIF:ImageUniqueID={uuid} already exists in file {filepath}.")

        # Else, no uuid was read by exiftool, or overwrite has been set to True.
        else:
            et.execute(f'-ImageUniqueID={mint_uuid()}'.encode(), filepath.encode())
            try:
                os.remove(filepath+"_original")
            except FileNotFoundError:
                pass

            # Here, we only report back if the image file's uuid was updated.
            uuid = et.get_tag('ImageUniqueID', filepath)
            if uuid is not None:
                print(f"Wrote tag EXIF:ImageUniqueID={uuid} to file {filepath}.")
    return uuid

def pool_metadata(tagfile, normalized_catalog):
    """Collects key-value pairs from a given metadata tag file (here '.csv' or '.tsv'),
    then updates a given normalized catalog. TODO Add args for json or xml.

    :tagfile: Relative path to metadata file.
    :normalized_catalog: Dictionary to write out key-value pairs.
    :returns: Updated content dictionary.

    """
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
                print('CSV Sniffer failed to parse file: {}, error: {}'.format(tagfile, e))

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
        print('Syntax error: key-value pair in file: {}, line {}: {}'.format(
            tagfile, reader.line_num, e))

    # Return normalized_catalog updated with key/value pairs from tagfile.
    return normalized_catalog

def get_normalized_catalog(ingest_dir, overwrite=False):
    """Catalogs the files and directories below the ingest_dir (relative path),
    given '.csv' or '.tsv' metadata (TODO or '.json') in the directory tree.

    :pool_metadata: "metadata gathering" function defined below.

    :ingest_dir: Relative path to directory to be cataloged. Should be a directory.
    :returns: Nested json describing files, directories, and metadata.

    """

    # Suppose ingest_dir is a parent.
    parent = Path(ingest_dir)

    # Initialize dictionary.
    normalized_catalog = {} 

    if parent.is_dir():

        normalized_catalog['contents'] = list()

        # List relative paths to children.
        children = map(lambda x : os.path.join(parent, x), 
                sorted(os.listdir(parent)))

        # Recurse down by calling `get_normalized_catalog` for each child.
        # We reserve the key 'contents' for inclusion of lists of child
        # dictionaries. The key 'contents' should appear 0 or 1 times in
        # each child dictionary.

        for child in children:
            if not os.path.basename(child).startswith("."):
                normalized_catalog['contents'].append(
                        get_normalized_catalog(child, overwrite=overwrite))
            # Determine if `child` is a metadata tag file, and if so, in which input format.
            _, ext = os.path.splitext(child)
            # TODO Test for xml or json or ini files
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

    breakpoint()
    return normalized_catalog

def tail_flatten_list(flat_list, nested_lists):
    if nested_lists == []:
        return flat_list
    new_nested_lists = []
    new_flat_list = flat_list
    for nested_list in nested_lists:
        items = filter(lambda I: not isinstance(I, list), nested_list)
        lists = filter(lambda L: isinstance(L, list), nested_list) 
        new_flat_list.extend(items)
        new_nested_lists.extend(lists)
    return tail_flatten_list(new_flat_list, new_nested_lists)

def flatten_list(nested_list):
      items = list(filter(lambda I: not isinstance(I, list), nested_list))
      lists = list(filter(lambda L: isinstance(L, list), nested_list))
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
    ts = str(datetime.now().strftime("%Y-%m-%d-%H%M%S"))
    with open(os.path.join(output_dir, f'{ts}-catalog.json'), 'w') as fp:
        json.dump(catalog, fp, indent=4)

def read_timestamped_catalog(output_dir):
    try:
        most_recent_catalog = sorted(glob.glob(
            os.path.join(output_dir,'*-catalog.json'))).pop()
        with open(most_recent_catalog, 'r') as fp:
            catalog = json.load(fp)
        return catalog
    except IndexError: 
        print(f"{output_dir} does not contain a file ending in '*-catalog.json'.")
