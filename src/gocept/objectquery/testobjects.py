# Copyright (c) 2007-2008 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

import persistent
import persistent.list
import transaction

from ZODB import MappingStorage, DB


class User(persistent.Persistent):
    """A user with an access list."""

    name = ""
    age = 0

    def __init__(self):
        self.owns = persistent.list.PersistentList()

class Car(persistent.Persistent):
    """A car."""

    manufacturer = None
    model = ""
    color = "silver"

class Company(persistent.Persistent):
    """The manufacturer of a car."""

    name = ""
    location = ""


storage = MappingStorage.MappingStorage()
db = DB(storage)
conn = db.open()
dbroot = conn.root()

dbroot['Users'] = persistent.list.PersistentList()

Tom = User()
Tom.name = "Tom"
Tom.age = 23

Max = User()
Max.name = "Max"
Max.age = 17

Susi = User()
Susi.name = "Susi"
Susi.age = 31

Focus = Car()
Focus.model = "Focus"
Focus.color = "red"

Tom.owns.append(Focus)
Susi.owns.append(Focus)

Boxter = Car()
Boxter.model = "Boxter"
Boxter.color = "black"

Max.owns.append(Boxter)

Ford = Company()
Ford.name = "Ford"
Ford.location = "USA"

Focus.manufacturer = Ford

Porsche = Company()
Porsche.name = "Porsche"
Porsche.location = "Germany"

Boxter.manufacturer = Porsche



dbroot['Users'].extend((Tom, Susi, Max))

testdb = dbroot['Users']




from persistent import Persistent
from persistent.list import PersistentList


class Dummy(Persistent):
    """ Dummy object """
    def __init__(self, ref=None):
        self.ref = PersistentList()
        if ref is None:
            return
        for elem in ref:
            self.ref.append(elem)

#
# testobjects for processor testcases
#

class Telephone(Dummy):
    def __init__(self, number="", ref=None):
        super(self.__class__, self).__init__(ref)
        self.number = number

class Person(Dummy):
    def __init__(self, name="", private=None, work=None):
        super(self.__class__, self).__init__(private)
        self.private = self.ref[:]
        super(self.__class__, self).__init__(work)
        self.work = self.ref[:]
        self.name = name

class Address(Dummy):
    def __init__(self, street="", city="", floor="", ref=None):
        super(self.__class__, self).__init__(ref)
        self.street = street
        self.city = city
        self.floor = floor

class AddressBook(Dummy):
    pass

#
# testobjects for Kleene Closure doctests
#


class Root(Dummy):
    pass

class Plone(Dummy):
    pass

class Folder(Dummy):
    pass

class Document(Dummy):
    pass
