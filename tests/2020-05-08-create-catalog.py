#! /usr/bin/env python3
#
# 2020-05-08 
# Colton Grainger 
# CC-0 Public Domain

"""
The ingest directory parses its contents and writes an unnormalized catalog at
its root.
"""

from context import imagearchive
from imagearchive.core import setup_directories
from imagearchive.core import setup_database_engine

ingest, data, output = setup_directories()
engine = setup_database_engine()

from imagearchive.schema import Base, Archive, Platform, Document, Image
