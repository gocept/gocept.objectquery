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
        self.index[key].insert(value)
        transaction.commit()

    def delete(self, key, value):
        """ Delete value from key. """
        self.index[key].remove(value)
        if len(self.index[key]) == 0:
            del self.index[key]
        transaction.commit()

    def get(self, key):
        """ Get the IndexItem for a given key. """
        return list(self.index[key])

    def has_key(self, key):
        """ Return True if key is present, otherwise False. """
        if self.index.has_key(key):
            return True
        return False

class ClassIndex(OOIndex):
    """ Maps strings (classnames) to an IndexItem object. """
    pass

class AttributeIndex(OOIndex):
    """ Maps strings (attributenames) to an IndexItem object. """
    pass

class StructureIndex(OOIndex):
    """ Stores information about the relationship between objects. 

    It allows you to determine the parent-child-relationship between two
    objects without having to touch the objects in the ZODB.
    """

    def insert(self, key, parent):
        """ Insert key under parent. """
        tail = (key, )
        new_path = []
        if self.index.has_key(parent):
            for elem in self.get(parent)[:]:
                new_path.append(elem + tail)
        else:
            new_path.append(tail)
        if not self.has_key(key):
            self.index[key] = []
        self.index[key].extend(new_path)
        transaction.commit()

    def delete(self, key, parent=None):
        """ Delete the key from the index. """
        if parent is None:
            del self.index[key]
        else:
            path = self.index[key][:]
            for elem in path:
                if elem[-2] == parent:
                    path.remove(elem)
            if len(path) == 0:
                del self.index[key]
            else:
                self.index[key] = path
        transaction.commit()

    def get(self, key):
        """ Return the path for a given key. """
        path = self.index[key]
        # Purge, if a predecessor has been deleted
        for elem in path:
            for i in range(len(elem)-1):
                if not self._check_path(elem[i], elem[i+1]):
                    self.delete(key, elem[-2])
        return self.index[key]

    def is_parent(self, key1, key2):
        """ Check if key1 is a direct predecessor of key2. """
        for elem1 in self.get(key1):
            for elem2 in self.get(key2):
                if len(elem1) + 1 == len(elem2):
                    return True
        return False

    def is_child(self, key1, key2):
        """ Check if key1 is a direct successor of key2. """
        for elem1 in self.get(key1):
            for elem2 in self.get(key2):
                if len(elem1) == len(elem2) + 1:
                    return True
        return False

    def is_predecessor(self, key1, key2):
        """ Check is key1 is a predecessor of key2. """
        for elem1 in self.get(key1):
            for elem2 in self.get(key2):
                size_of_elem1 = len(elem1)
                if size_of_elem1 >= len(elem2):
                    return False
                for i in range(size_of_elem1):
                    if elem1[i] != elem2[i]:
                        return False
        return True

    def is_successor(self, key1, key2):
        """ Check is key1 is a successor of key2. """
        for elem1 in self.get(key1):
            for elem2 in self.get(key2):
                size_of_elem2 = len(elem2)
                if len(elem1) <= size_of_elem2:
                    return False
                for i in range(size_of_elem2):
                    if elem1[i] != elem2[i]:
                        return False
        return True

    def _check_path(self, key1, key2):
        """ Check if key1 and key2 are directly connected. """
        if not self.has_key(key2):
            return False
        for elem in self.index[key2]:
            if key1 in elem:
                if elem[-2] == key1:
                    return True
        return False

