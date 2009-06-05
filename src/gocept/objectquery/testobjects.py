# Copyright (c) 2007-2009 gocept gmbh & co. kg
# See also LICENSE.txt

import persistent

# class definitions for the test db

class Obj(persistent.Persistent):
    # A very lightweight persistent object for testing purposes.
    pass


class Library(persistent.Persistent):

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

    def __init__(self, author, title, written, isbn):
        self.author = author
        self.title = title
        self.written = written
        self.isbn = isbn


class Person(persistent.Persistent):

    def __init__(self, name):
        self.name = name



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
