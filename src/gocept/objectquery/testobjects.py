# Copyright (c) 2007 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

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

class Telephone(Dummy):
    def __init__(self, number="", ref=None):
        super(self.__class__, self).__init__(ref)
        self.number = number

class Person(Dummy):
    def __init__(self, name="", ref=None):
        super(self.__class__, self).__init__(ref)
        self.name = name

class Address(Dummy):
    def __init__(self, street="", city="", ref=None):
        super(self.__class__, self).__init__(ref)
        self.street = street
        self.city = city
