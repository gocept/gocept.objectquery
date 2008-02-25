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
        keyname = "_is_" + self.__class__.__name__
        if not dbroot.has_key(keyname):
            dbroot[keyname] = OOBTree()
        self.index = dbroot[keyname]

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

    def insert(self, key, parent=None):
        """ Insert key under parent. """
        if key == 0:
            raise ValueError("Key must be > 0.")
        if parent is None:
            parent = 0
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
        for child in self.index['childs'][key]:
            self._update_childs(child, new_path, [key])
        transaction.commit()

    def delete(self, key, parent=None):
        """ Delete the key from the index. """
        if parent == 0:
            parent = None
        for elem in self.index[key][:]:
            if parent is None or ( len(elem) > 1 and elem[-2] == parent ):
                if len(elem) > 1 and key in self.index['childs'][elem[-2]]:
                    self.index['childs'][elem[-2]].remove(key)
                self.index[key].remove(elem)
                self._purge(key, elem)
        if len(self.index[key]) == 0:
            del self.index[key]
            del self.index['childs'][key]
        transaction.commit()

    def is_parent(self, key1, key2):
        """ Check if key1 is a direct predecessor of key2. """
        for elem1 in self.get(key1):
            for elem2 in self.get(key2):
                if len(elem1) + 1 == len(elem2) and\
                    self._check_path(elem1, elem2):
                    return True
        return False

    def is_child(self, key1, key2):
        """ Check if key1 is a direct successor of key2. """
        for elem1 in self.get(key1):
            for elem2 in self.get(key2):
                if len(elem1) == len(elem2) + 1 and\
                    self._check_path(elem2, elem1):
                    return True
        return False

    def is_predecessor(self, key1, key2):
        """ Check if key1 is a predecessor of key2. """
        for elem1 in self.get(key1):
            for elem2 in self.get(key2):
                if self._check_path(elem1, elem2):
                    return True
        return False

    def is_successor(self, key1, key2):
        """ Check if key1 is a successor of key2. """
        for elem1 in self.get(key1):
            for elem2 in self.get(key2):
                if self._check_path(elem2, elem1):
                    return True
        return False

    def _update_childs(self, key, path_dict, cycle_prevention):
        """ Update childs of inserted nodes with the new path. """
        tail = (key, )
        new_path = []
        for elem in path_dict:
            new_path.append(elem + tail)
        self.index[key].extend(new_path)
        for child in self.index['childs'][key]:
            if child not in cycle_prevention:
                cycle_prevention.append(child)
                self._update_childs(child, new_path, cycle_prevention)

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

    def get(self, key):
        """ Return the path for a given key. """
        if key == 0:
            raise ValueError("Key must be > 0.")
        return self.index[key]

    def _check_path(self, path1, path2):
        """ Check if path1 is reachable by path2. """
        if len(path1) > len(path2):
            return False
        for i in range(len(path1)):
            if path1[i] != path2[i]:
                return False
        return True
