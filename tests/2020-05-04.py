#! /usr/bin/env python3
#
# 2020-04-20 
# Colton Grainger 
# CC-0 Public Domain

"""
Prototypical Image Archive
"""

from context import imagearchive
from imagearchive.schema import Base, Archive, Platform, Document, Image
from imagearchive.config import setup_directories, setup_database_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime, date

engine = setup_database_engine()
ingest_dir, data_dir, output_dir = setup_directories()

Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()

##

nara = Archive()
nara.name='National Archives and Records Administration'
nara.country_code='USA'
session.add(nara)
print(session.query(Archive).all())

##

parameters = {
        'name': 'USCG Storis',
        'country_code':'USA'
        }
storis = Platform(**parameters)
session.add(storis)
print(session.query(Platform).all())

##

logbook = Document()
logbook.start_date = date.fromisoformat('1860-05-01')
logbook.end_date = date.fromisoformat('1860-05-04')
logbook.archive = nara
logbook.related_identifier = '38547962'
logbook.related_identifier_type = 'NARA ID'

logbook.platform = storis
session.add(logbook)
print(session.query(Document).all())

##

ncar = Archive()
ncar.name='National Center for Atmospheric Research'
ncar.country_code='USA'
session.add(ncar)

notebook = Document(
        start_date=date.fromisoformat('2020-05-01'),
        end_date = date.fromisoformat('2020-05-04'),
        archive = ncar
        )
session.add(notebook)

##

pic = Image(id='269c12943c7211ea9a8708119645fa1c')
pic.file_size = 4024
pic.file_media_type='image/jpeg'
pic.file_created_datetime = datetime.fromisoformat('2000-01-01T07:34:57')
pic.file_modified_datetime = datetime.fromisoformat('2000-01-01T07:34:57')
pic.file_original_name='storis-wmec-38-1957-logbooks_0135.JPG'
pic.document = logbook
session.add(pic)
print(session.query(Image).all())

##
