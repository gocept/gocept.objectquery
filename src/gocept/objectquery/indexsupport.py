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

    def __repr__(self):
        return str(list(self))


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

    def __init__(self, dbroot):
        """ """
        super(self.__class__, self).__init__(dbroot)
        self.index['childs'] = OOBTree()    # Childindex, needed for deletion

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
        if not self.index['childs'].has_key(parent):
            self.index['childs'][parent] = IndexItem()
        self.index['childs'][parent].insert(key)
        if not self.index['childs'].has_key(key):
            self.index['childs'][key] = IndexItem()
        transaction.commit()

    def _purge(self, key, tupel):
        """ Purge the child nodes of key with tupel. """
        for child in self.index['childs'][key]:
            if self.index.has_key(child):
                for elem in self.index[child][:]:
                    if elem[:-1] == tupel:
                        self.index[child].remove(elem)
                        self._purge(child, elem)
                if len(self.index[child]) == 0:
                    self.delete(child, key)

    def delete(self, key, parent=None):
        """ Delete the key from the index. """
        if parent == 0:
            parent = None
        for elem in self.index[key][:]:
            if parent is None or elem[-2] == parent:
                if len(elem) > 1:
                    self.index['childs'][elem[-2]].remove(key)
                self.index[key].remove(elem)
                self._purge(key, elem)
        if len(self.index[key]) == 0:
            del self.index[key]
            del self.index['childs'][key]
        transaction.commit()

    def get(self, key):
        """ Return the path for a given key. """
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
