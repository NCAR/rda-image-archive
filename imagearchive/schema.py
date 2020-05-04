#! /usr/bin/env python3
#
# 2020-05-04 
# Colton Grainger 
# CC-0 Public Domain

"""
Object Relational Mapper
"""

from sqlalchemy import Column, Integer, String, Date, DateTime
from sqlalchemy import UniqueConstraint, ForeignKey
from sqlalchemy import func

from sqlalchemy.orm import relationship

from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.ext.declarative import declarative_base

class Base(object):
    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()

    __table_args__ = {'mysql_engine': 'InnoDB'}

    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime, default=func.now()) 

Base = declarative_base(cls=Base)

class Archive(Base):

    """Abstraction for archives as "original custodians" of documents"""

    name = Column(String(255))
    country_code = Column(String(3))

    def __repr__(self):
        return f"<Archive(name='{self.name}', "\
                + f"country_code='{self.country_code}')>"

class Platform(Base):

    """Abstraction for meteorological platforms as "original authors" of documents"""

    name = Column(String(255))
    country_code = Column(String(3))

    def __repr__(self):
        return f"<Platform(name='{self.name}', "\
                + f"country_code='{self.country_code}')>"

class Document(Base):

    """Abstraction for documents as linearly ordered collections of images"""

    id_within_archive = Column(String(255))
    id_within_archive_type = Column(String(55))
    start_date = Column(Date)
    end_date = Column(Date)
    license = Column(String(55), default='CC-0 Public Domain')

    def __repr__(self):
        return f"<Document(id_within_archive=('{self.id_within_archive}'), "\
                + f"id_within_archive_type=('{self.id_within_archive_type}'), "\
                + f"start_date=date.fromisoformat('{self.start_date}'), "\
                + f"end_date=date.fromisoformat('{self.end_date}'), "\
                + f"license='{self.license}')>"

    # add a relationship directive to access a documents's archive 
    archive_id = Column(Integer, ForeignKey('archive.id'))
    archive = relationship('Archive', back_populates='documents')

    # add a relationship directive to access a documents's platform
    platform_id = Column(Integer, ForeignKey('platform.id'))
    platform = relationship('Platform', back_populates='documents')

# add the converse relationship directive to the Archive class
Archive.documents = relationship('Document', order_by=Document.id,
        back_populates='archive', cascade='all, delete, delete-orphan')

# add the converse relationship directive to the Platform class
Platform.documents = relationship('Document', order_by=Document.id,
        back_populates='platform', cascade='all, delete, delete-orphan')

class Image(Base):

    """Abstraction for metadata corresponding to binary image files"""

    id = Column(String(36), primary_key=True)
    wid = Column(Integer)

    # add file-level metadata attributes
    file_size = Column(Integer) # number of bytes
    file_media_type = Column(String(10)) # e.g., 'image/tiff'
    file_created_datetime = Column(DateTime)
    file_modified_datetime = Column(DateTime)
    file_original_name = Column(String(255))

    document_id = Column(Integer, ForeignKey('document.id'))
    document = relationship('Document', back_populates='images')

    def __repr__(self):
        return f"<Image(id='{self.id}', "\
            + f"file_size='{self.file_size}', "\
            + f"file_media_type='{self.file_media_type}', "\
            + "file_created_datetime=datetime.fromisoformat"\
            + f"('{self.file_created_datetime}'), "\
            + "file_modified_datetime=datetime.fromisoformat"\
            + f"('{self.file_modified_datetime}'), "\
            + f"file_original_name='{self.file_original_name}')>"
        
Document.images = relationship('Image', order_by=Image.id,
        back_populates='document', cascade='all, delete, delete-orphan')
