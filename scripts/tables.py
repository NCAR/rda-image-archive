#! /usr/bin/env python3
#
# 2020-02-05 
# Colton Grainger 
# CC-0 Public Domain

"""
Initialize archive, platform, document, and image tables.
"""

from sqlalchemy import Table, Column, MetaData
from sqlalchemy import UniqueConstraint, ForeignKey
from sqlalchemy import Integer, String, Date
from sqlalchemy.types import Enum

metadata = MetaData()

archive = Table('archive', metadata,
    Column('archive_id', Integer(), primary_key=True),
    Column('name', String(50)),
    Column('host_country', String(3)),
    UniqueConstraint('name', 'host_country',
        name='uix_archive_name_and_host_country')
)

platform = Table('platform', metadata,
    Column('platform_id', Integer(), primary_key=True),
    Column('name', String(50)),
    Column('host_country', String(3)),
    UniqueConstraint('name','host_country',
        name='uix_platform_name_and_host_country')
)
 
document = Table('document', metadata,
    Column('document_id', Integer(), primary_key=True),
    Column('platform_id', ForeignKey('platform.platform_id')),
    Column('archive_id', ForeignKey('archive.archive_id')),
    Column('id_within_archive', String(255), nullable=False),
    Column('id_within_archive_type', String(50), nullable=False),
    # NARA ID, ARK, ISBN, DOI, etc. 
    # Refer to DataCite Metadata Schema 4.2 relatedIdentifierType.
    Column('start_date', Date(), nullable=False),
    Column('end_date', Date(), nullable=False),
    Column('standardized_region_list', 
        Enum(
            'north atlantic',
            'south atlantic',
            'north pacific',
            'south pacific',
            'north indian',
            'south indian',
            'antarctic',
            'arctic',
            'mediterranean',
            'black sea',
            'baltic sea',
            'persian gulf',
            'red sea'
        )
    # TODO utils.py cannot yet pass a SET of values to ENUM 2020-02-05
    ),
    # Steve Worley recommended this subset
    # of the CF standardized regions list. See the full list here:
    # http://cfconventions.org/Data/standardized-region-list.
    Column('rights_statement', String(50)),
    Column('contact_person', String(50)),
    Column('notes', String(255)),
    UniqueConstraint('id_within_archive_type','id_within_archive',
        name='uix_id_within_archive')
)

image = Table('image', metadata,
    Column('uuid', String(36), primary_key=True),
    Column('wid', String(255)),
    Column('document_id', ForeignKey('document.document_id')),
    Column('media_type', 
        Enum(
            'image/bmp',
            'image/gif',
            'image/jp2',
            'image/jpeg',
            'image/png',
            'image/tiff'
        )
    )
    # Column('file_size_in_bytes', Decimal(10))
    # TODO revise utils.py to check for file_size
    # Column('relative_order')
    # TODO determine relative order of document in logbook, 
    # or just check "between" semisequential uuids
)
