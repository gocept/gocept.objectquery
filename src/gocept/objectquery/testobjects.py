# Copyright (c) 2007-2008 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

import persistent
import persistent.list
import transaction

import ZODB.MappingStorage, ZODB.DB

# class definitions for the test db

class Library(persistent.Persistent):
    """ """

    def __init__(self, location, books=[]):
        self.location = location
        self.books = []
        for book in books:
            self.add_book(book)

    def add_book(self, book):
        self.books.append(book)
        self._p_changed = True

    def delete_book(self, book):
        self.books.remove(book)
        self._p_changed = True


class Book(persistent.Persistent):
    """ """

    def __init__(self, author, title, written, isbn):
        self.author = author
        self.title = title
        self.written = written
        self.isbn = isbn


class Person(persistent.Persistent):
    """ """

    def __init__(self, name):
        self.name = name


storage = ZODB.MappingStorage.MappingStorage()
db = ZODB.DB(storage)
conn = db.open()
dbroot = conn.root()

# Authors

p_orwell = Person(name="George Orwell")
p_lotze = Person(name="Thomas Lotze")
p_goethe = Person(name="Johann Wolfgang von Goethe")
p_weitershausen = Person(name="Philipp von Weitershausen")

# Books

b_1984 = Book(author=p_orwell,
              title="1984",
              written=1990,
              isbn=3548234100)

b_plone = Book(author=p_lotze,
               title="Plone-Benutzerhandbuch",
               written=2008,
               isbn=3939471038)

b_faust = Book(author=p_goethe,
               title="Faust",
               written=1811,
               isbn=3406552501)

b_farm = Book(author=p_orwell,
              title="Farm der Tiere",
              written=2002,
              isbn=3257201184)

b_zope = Book(author=p_weitershausen,
              title="Web Component Development with Zope 3",
              written=2007,
              isbn=3540338071)

# Libraries

l_halle = Library(location="Halle",
                  books=[b_1984, b_plone, b_farm, b_zope])

l_berlin = Library(location="Berlin",
                   books=[b_1984, b_plone, b_faust, b_farm, b_zope])

l_chester = Library(location="Chester",
                    books=[b_1984, b_faust, b_farm])


dbroot['librarydb'] = persistent.list.PersistentList()
dbroot['librarydb'].extend([l_halle, l_berlin, l_chester])

librarydb = dbroot['librarydb']

transaction.commit()

class Dummy(persistent.Persistent):
    """An object with an id and a reference list."""
    def __init__(self, id=None, ref=[]):
        self.id = id
        self.ref = []
        self.ref.extend(ref)

    def add_item(self, item):
        self.ref.append(item)
        self._p_changed = True


# needed for kleen closure tests in processor.txt

class Root(Dummy):
    pass

class Plone(Dummy):
    pass

class Folder(Dummy):
    pass

class Document(Dummy):
    pass
