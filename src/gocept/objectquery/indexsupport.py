# Copyright (c) 2007-2008 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

import types
import zope.interface
import transaction
import ZODB.Connection
import gocept.objectquery.interfaces
from persistent import Persistent
from BTrees.OOBTree import OOBTree, OOTreeSet


class IndexItem(OOTreeSet):
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

    def delete(self, key, value):
        """ Delete value from key. """
        if not self.index.has_key(key):
            return
        if value not in self.index[key]:
            return
        self.index[key].remove(value)
        if len(self.index[key]) == 0:
            del self.index[key]

    def get(self, key):
        """ Get the IndexItem for a given key. """
        if key in self.index:
            return list(self.index[key])
        return []

    def has_key(self, key):
        """ Return True if key is present, otherwise False. """
        return key in self.index

    def all(self):
        """ Return all objects from the index. """
        allitems = []
        for indexitem in list(self.index.keys()):
            for elem in self.get(indexitem):
                if elem not in allitems:
                    allitems.append(elem)
        return allitems

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
        super(StructureIndex, self).__init__(dbroot)
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
        for path in new_path:
            if path not in self.index[key]:
                self.index[key].append(path)
        if not self.index['childs'].has_key(parent):
            self.index['childs'][parent] = IndexItem()
        self.index['childs'][parent].insert(key)
        if not self.index['childs'].has_key(key):
            self.index['childs'][key] = IndexItem()
        for child in self.index['childs'][key]:
            self._update_childs(child, new_path, [key])

    def delete(self, key, parent=None):
        """ Delete the key from the index. """
        if parent == 0:
            parent = None
        if not self.index.has_key(key):
            return
        for elem in self.index[key][:]:
            if parent is None or ( len(elem) > 1 and elem[-2] == parent ):
                if len(elem) > 1 and key in self.index['childs'].get(elem[-2],[]):
                    self.index['childs'][elem[-2]].remove(key)
                if elem in self.index.get(key, []):
                    self.index[key].remove(elem)
                self._purge(key, elem)
        if self.index.has_key(key) and len(self.index[key]) == 0:
            del self.index[key]
            del self.index['childs'][key]

    def is_child(self, key1, key2):
        """ Check if key1 is a direct successor of key2. """
        if not key1 or not key2:
            return True   # empty keys return True (see KCJoin)
        for elem1 in self.get(key1):
            for elem2 in self.get(key2):
                if len(elem1) == len(elem2) + 1 and\
                    self._check_path(elem2, elem1):
                    return True
        return False

    def is_successor(self, key1, key2):
        """ Check if key1 is a successor of key2. """
        for elem1 in self.get(key1):
            for elem2 in self.get(key2):
                if self._check_path(elem2, elem1):
                    return True
        return False

    def get(self, key):
        """ Return the path for a given key. """
        if key == 0:
            raise ValueError("Key must be > 0.")
        return self.index[key]

    def validate(self, key, indexlist):
        """ Return True if keys index is a part of indexlist. """
        for elem in self.get(key):
            for index in indexlist:
                if elem[:len(index)] == index:
                    return True
        return False

    def root(self):
        """ Return the root object. """
        return list(self.index['childs'][0])[0]

    def _update_childs(self, key, path_dict, cycle_prevention):
        """ Update childs of inserted nodes with the new path. """
        tail = (key, )
        new_path = []
        for elem in path_dict:
            new_path.append(elem + tail)
        for path in new_path:
            if path not in self.index[key]:
                self.index[key].append(path)
        for child in self.index['childs'][key]:
            if child not in cycle_prevention:
                cycle_prevention.append(child)
                self._update_childs(child, new_path, cycle_prevention)

    def _purge(self, key, tupel):
        """ Purge the child nodes of key with tupel. """
        for child in self.index['childs'].get(key, []):
            if self.index.has_key(child):
                for elem in self.index[child][:]:
                    if elem[:-1] == tupel:
                        self.index[child].remove(elem)
                        self._purge(child, elem)
                if len(self.index.get(child, [])) == 0:
                    self.delete(child, key)

    def _check_path(self, path1, path2):
        """ Check if path1 is reachable by path2. """
        if len(path1) > len(path2):
            return False
        for i in range(len(path1)):
            if path1[i] != path2[i]:
                return False
        return True


class IndexSynchronizer(object):
    """A transaction synchronizer for automatically updating the indexes on
    transaction boundaries.
    """

    zope.interface.implements(transaction.interfaces.ISynchronizer)

    def beforeCompletion(self, transaction):
        """Hook that is called by the transaction at the start of a commit.
        """
        for data_manager in transaction._resources:
            if not isinstance(data_manager, ZODB.Connection.Connection):
                continue
            collection = zope.component.getUtility(
                gocept.objectquery.interfaces.IObjectCollection)
            for obj in data_manager._registered_objects:
                collection.add(obj)


    def afterCompletion(self, transaction):
        """Hook that is called by the transaction after completing a commit.
        """
        pass

    def newTransaction(self, transaction):
        """Hook that is called at the start of a transaction.
        """
        pass

