#! /usr/bin/env python3
#
# 2020-05-04 
# Colton Grainger 
# CC-0 Public Domain

"""
Defines classes mapped to relational database tables, using SQLAlchemy's  
Declarative system. docs.sqlalchemy.org/en/13/orm/extensions/declarative/
"""

from sqlalchemy import Table, Column
from sqlalchemy import Integer, String, Date, DateTime, JSON
from sqlalchemy import UniqueConstraint, ForeignKey
from sqlalchemy import func

from sqlalchemy.orm import relationship

from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.ext.declarative import declarative_base

class Base(object):
    """
    An augmented Base class 

    1. to name tables (e.g., `class Archive(Base)` will be mapped by the ORM to
       the table `archive` in the database), 
    2. to set MySQL table options, and
    3. to define some common sense fields in each table (an integer primary
       key and created_at datetime timestamp).

    Note the Image class will redefine its primary key to be 32-char hexadecimal
    string. See also:

    docs.sqlalchemy.org/en/13/orm/extensions/declarative/mixins.html#augmenting-the-base

    """

    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()

    __table_args__ = {'mysql_engine': 'InnoDB'}

    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime, default=func.now()) 

# first instantiate the augmented Base to inherit from
Base = declarative_base(cls=Base)

# then inherit from the instatiated Base class
class Archive(Base):

    """ 
    Abstraction for archives as arbitrary collections of documents.

    A good criteria for metadata providers (if determining "what archive does
    this document belong to?" is not obvious) is to ask:

        What *social* entity was responsible for this document for the greatest length of
        time between the point (i) when meteorological data was observed and
        recorded in it and the point (ii) when I came into first contact with it?

    Archive.name is an archive's formal name.

        If this archive has a Wikipedia article dedicated to it,
        what is the title of that article? If not, what would be?

    Archive.country_code is a (lowercase) ISO 3166-1 Alpha-3 code for
    the country that hosts an archive. A controlled vocabulary is here:

        https://en.wikipedia.org/wiki/ISO_3166-1_alpha-3

    There is a unique constraint on (Archive.name, Archive.country_code).

    """

    __table_args__ = (UniqueConstraint('name', 'country_code',
        name='uix_archive_name_and_country_code'),) + (Base.__table_args__,)
        
    name = Column(String(255))
    country_code = Column(String(3))

    def __repr__(self):
        return f"<Archive(name='{self.name}', "\
                + f"country_code='{self.country_code}')>"

class Platform(Base):

    """
    Abstraction for platforms as arbitrary collections of documents.

    A good criteria for metadata providers is to ask:

        What *spatial* entity was responsible for recording the meteorological
        observations in this document? E.g., a single ship or weather station.

    Platform.name is a platform's formal name (see note). C.f.
        
        https://en.wikipedia.org/wiki/Wikipedia:Naming_conventions_(ships)

    Platform.country_code is the (lowercase) ISO 3166-1 Alpha-3 code for
    the country that hosted the platform. A controlled vocabulary is
    here:

        https://en.wikipedia.org/wiki/ISO_3166-1_alpha-3

    There is a unique constraint on (Platform.name, Platform.country_code).

    Note: Philip Brohan shared a few edge cases from his research (e.g., images
    containing meteorological data from every weather station on the Indian
    subcontinent). In these cases I suggest Platform.name=str(), and indicate
    only the country_code. To accommodate such edge cases, the current
    one-to-many relationship Platform->Document fails and would need to be
    revised for Platform<->Document.

    """

    __table_args__ = (UniqueConstraint('name', 'country_code',
        name='uix_platform_name_and_country_code'),) + (Base.__table_args__,)

    name = Column(String(255))
    country_code = Column(String(3))

    def __repr__(self):
        return f"<Platform(name='{self.name}', "\
                + f"country_code='{self.country_code}')>"

# We also define an association table for arbitrary document-level tags.
document_tags = Table('document_tags', Base.metadata,
    Column('document_id', ForeignKey('document.id'), primary_key=True),
    Column('tag_id', ForeignKey('tag.id'), primary_key=True)
)

class Document(Base):

    """
    Abstraction for documents as ordered collections of images.

    Document.start_date and Document.end_date are datetime.date types.

        Typing forces us to upcast years to dates, e.g., if an image's metadata
        reads "document.start_date, 1860", during ingest Document.start_Date
        will be arbitrarily assigned to datetime.fromisoformat("1860-01-01").
        Specifying accurate dates would be useful if one wanted to interpolate
        the specific date of an image in a document by relative order between
        the first image containing meteorological data and the last image
        containing meteorological data, provided that each image represents
        a certain fixed length time-series, e.g., 12, 24, or 48 hours.

    Document.license is a license string, defaulting to 'CC-0 Public Domain'. 
    If one wanted to implement a controlled vocabulary for these, see for example:

        https://creativecommons.org/licenses/

    Document.related_identifier and Document.related_identifier_type are
    strings identifying how a document "belongs" to an archive. If the former
    is defined, the later ought to be as well. If one wanted to implement a
    controlled vocabulary for these (ARK, ISBN, DOI, etc.), see for example:

        DataCite Metadata Schema 4.3 
        Appendix 1: 'relatedIdentifierType'
        https://doi.org/10.14454/7xq3-zf69

    """

    start_date = Column(Date)
    end_date = Column(Date)
    license = Column(String(55), default='CC-0 Public Domain')
    related_identifier = Column(String(255))
    related_identifier_type = Column(String(10))

    def __repr__(self):
        return f"<Document(related_identifier=('{self.related_identifier}'), "\
                + f"related_identifier_type=('{self.related_identifier_type}'), "\
                + f"start_date=date.fromisoformat('{self.start_date}'), "\
                + f"end_date=date.fromisoformat('{self.end_date}'), "\
                + f"license='{self.license}')>"

    # many to many Document<->Tag
    tags = relationship('Tag', secondary=document_tags,
                            back_populates='documents')

    # one to many Document->Archive
    archive_id = Column(Integer, ForeignKey('archive.id'))
    archive = relationship('Archive', back_populates='documents')

    # one to many Document->Platform
    platform_id = Column(Integer, ForeignKey('platform.id'))
    platform = relationship('Platform', back_populates='documents')

# add the converse relationship directive to the Archive class
Archive.documents = relationship('Document', 
        order_by=Document.id,
        back_populates='archive', 
        cascade='all, delete, delete-orphan',
        # A single archive might have many documents. "To be able to filter
        # results further so as not to load the entire collection, we use a
        # setting accepted by relationship() called lazy='dynamic', which
        # configures an alternate loader strategy on the attribute."
        # docs.sqlalchemy.org/en/13/orm/relationship_api.html#sqlalchemy.orm.relationship.params.lazy
        lazy="dynamic") 

# add the converse relationship directive to the Platform class
Platform.documents = relationship('Document', 
        order_by=Document.id,
        back_populates='platform', 
        cascade='all, delete, delete-orphan')

class Image(Base):

    """
    Abstraction for images as "pages" of documents and the associated file-level
    metadata, e.g., uuid, path on disk, modify datetime.

    Image.id is a 32-char hexadecimal uuid (see note), generated during ingest
    and written to a binary image file's EXIF metadata.

    Image.wid is for dsarch interoperability.

    Image.file_size is an image's file size in number of bytes.

    Image.file_media_type is an image's MIME type, generated during ingest from
    python-magic, e.g., 'image/tiff'.

    Both Image.file_created_datetime and Image.file_modified_datetime are
    datatime.datetime types, these are read from an image's EXIF metadata.

    Image.file_original_name is an image file's basename at time of ingest, 
    and is presently used for sequencing images within a document.

    Note: While one might, for Image.id, expect a 36-char uuid with hyphens rather than a
    32-char uuid without, this was done with mind to the following: If
    eventually storing some 3 million images is slowing down MySQL
    indexing on the primary key, one could re-implement Image.id as type
    Binary(16) (it's the same in SQLAlchemy as it is in MySQL): casting to a
    16-byte representation from the existing 32-char hexadecimal uuid and using a
    @property decorator to transform between the two.

    """

    id = Column(String(36), primary_key=True)
    wid = Column(Integer)
    file_size = Column(Integer) 
    file_media_type = Column(String(10)) 
    file_created_datetime = Column(DateTime)
    file_modified_datetime = Column(DateTime)
    file_original_name = Column(String(255))

    def __repr__(self):
        return f"<Image(id='{self.id}', "\
            + f"file_size='{self.file_size}', "\
            + f"file_media_type='{self.file_media_type}', "\
            + "file_created_datetime=datetime.fromisoformat"\
            + f"('{self.file_created_datetime}'), "\
            + "file_modified_datetime=datetime.fromisoformat"\
            + f"('{self.file_modified_datetime}'), "\
            + f"file_original_name='{self.file_original_name}')>"
        
    document_id = Column(Integer, ForeignKey('document.id'))
    document = relationship('Document', back_populates='images')

Document.images = relationship('Image', order_by=Image.id,
        back_populates='document', cascade='all, delete, delete-orphan')

class Tag(Base):

    """
    Abstraction for (controlled vocabulary) document tags.

    For example, to at least know in which ocean basin a document has
    observations from, Steve Worley recommended this subset of the CF
    standardized regions list as an initial controlled vocabulary:

    'north-atlantic', 'south-atlantic', 'north-pacific', 'south-pacific',
    'north-indian', 'south-indian', 'antarctic', 'arctic', 'mediterranean',
    'black-sea', 'baltic-sea', 'persian-gulf', 'red-sea'

    See the full list here: 

        http://cfconventions.org/Data/standardized-region-list

    """
   
    name = Column(String(50), nullable=False, unique=True)

    def __repr__(self):
        return f"<Tag(name='{self.name}')>"

    documents = relationship('Document', secondary=document_tags,
            back_populates='tags')

# TODO enhance class Observation in one-to-many relationship Image->Observation
# with metadata fields, for example, described in:
# github.com/NCAR/rda-image-archive-dev/blob/master/schema/observation.sql

class Observation(Base):

    """
    Abstraction for observations made on individual images.

    Observation.json is an arbitrary JSON type, intended to capture any metadata
    refinements made during an image's transcription.

    JSON is provided as a facade for vendor-specific JSON types. Since it
    supports JSON SQL operations, it only works on backends that have an
    actual JSON type, currently:

        PostgreSQL
        MySQL as of version 5.7 (MariaDB as of the 10.2 series does not)
        SQLite as of version 3.9

    To implement a controlled vocabulary for this attribute, or to abandon
    this attribute in favor of more specific meteorological metadata, see:

    1. Sec. 4.2.1 "Elements observed", WMO-No. 8 (2010 update)
       lwww.wmo.int/images/prog/www/IMOP/CIMO-Guide.html 

    2. github.com/NCAR/rda-image-archive-dev/blob/master/schema/observation.sql

    """

    json = Column(JSON)

    image_id = Column(Integer, ForeignKey('image.id'))
    image = relationship('image', back_populates='observations')

Image.observations = relationship('Observation', order_by=Observation.id,
        back_populates='documents', cascade='all, delete, delete-orphan')
