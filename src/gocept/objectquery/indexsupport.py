# Copyright (c) 2007 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

import types
from persistent import Persistent
from BTrees.OOBTree import OOBTree
from BTrees.IIBTree import IITreeSet
import transaction

class IndexItem(IITreeSet):
    """ Holds any number of integer values. """
    pass

class OOIndex(Persistent):
    """ A dummy object to IndexItem mapping index structure. """

    def __init__(self, dbroot):
        """ """
        classname = self.__class__.__name__
        if not dbroot.has_key(classname):
            dbroot[classname] = OOBTree()
        self.index = dbroot[classname]

    def insert(self, key, value):
        """ Insert value under key into the index. """
        if not self.index.has_key(key):
            self.index[key] = IndexItem()
        self.index[key].insert(value._p_oid)
        transaction.commit()

    def delete(self, key, value):
        """ Delete value from key. """
        self.index[key].remove(value._p_oid)
        if len(self.index[key]) == 0:
            self.index.remove(key)

class ClassIndex(OOIndex):
    """ Maps strings (classnames) to an IndexItem object. """
    pass

class AttributeIndex(OOIndex):
    """ Maps strings (attributenames) to an IndexItem object. """
    pass
