#! /usr/bin/env python3
#
# 2020-04-22
# Colton Grainger 
# CC-0 Public Domain

from context import imagearchive
from imagearchive.core import Base, Author

##

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# The sessionmaker factory should be used just once in an application's global
# scope, and treated like a configuration setting. Here, we create a new session
# associated with an in-memory SQLite database.

engine = create_engine('sqlite:///:memory:')

# defines a Session class with the 'bind' configuration supplied by 'sessionmaker'
Session = sessionmaker(bind=engine)

# creates a 'session' for our use from our generated Session class
session = Session()

# Base is a class defined in the imagearchive module
Base.metadata.create_all(engine)

##

# creating an instance of the Author class
colton = Author(name='Colton Grainger', email='colton.grainger@gmail.com', \
                organization='coltongrainger.com')

# adding the instance to the session
session.add(colton)

# committing to the session
session.commit()

# When commit() is called on the session, the author is actually inserted into
# the database. It also updates 'colton' with the primary key of the record in
# the database. We can see that by doing the following:
print('colton.author_id:', colton.author_id)

##


