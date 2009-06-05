# Copyright (c) 2007-2008 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

import zope.interface
import transaction
import ZODB.Connection
import gocept.objectquery.interfaces
import persistent
from BTrees.OOBTree import OOBTree, OOTreeSet
import gocept.objectquery.querysupport


parser = gocept.objectquery.querysupport.ObjectParser()


class OOIndex(persistent.Persistent):

    def __init__(self):
        """ """
        self._index = OOBTree()

    def insert(self, key, value):
        """ Insert value under key into the index. """
        if not self._index.has_key(key):
            self._index[key] = OOTreeSet()
        self._index[key].insert(value)

    def delete(self, key, value):
        """ Delete value from key. """
        if not self._index.has_key(key):
            return
        if value not in self._index[key]:
            return
        self._index[key].remove(value)
        if len(self._index[key]) == 0:
            del self._index[key]

    def get(self, key):
        """ Get the set for a given key. """
        if self.has_key(key):
            for item in self._index[key]:
                yield item

    def has_key(self, key):
        """ Return True if key is present, otherwise False. """
        return key in self._index

    def all(self):
        """ Return all objects from the index. """
        for set in self._index.values():
            for elem in set:
                yield elem


class ClassIndex(OOIndex):
    """Map class names to objects."""

    zope.interface.implements(gocept.objectquery.interfaces.IClassIndex)

    def _get_key(self, obj):
        return obj.__class__.__name__

    def index(self, obj):
        try:
            self.insert(self._get_key(obj), obj._p_oid)
        except AttributeError:
            pass

    def unindex(self, obj):
        self.delete(self._get_key(obj), obj._p_oid)

    def query(self, class_):
        # XXX Don't allow naive strings to be passed in
        if not isinstance(class_, str):
            class_ = class_.__name__
        return self.get(class_)


class AttributeIndex(OOIndex):

    zope.interface.implements(gocept.objectquery.interfaces.IAttributeIndex)

    def index(self, obj):
        for attr in parser.get_attributes(obj):
            self.insert(attr, obj._p_oid)

    def unindex(self, obj):
        # XXX Introduce reverse index.
        for obj_set in self._index.values():
            if obj._p_oid in obj_set:
                obj_set.remove(obj._p_oid)

    def query(self, attribute):
        return self.get(attribute)


def overlong_loop(path):
    """Check whether a given OID path contains a loop.

    Loops are paths that contain a sub-path consecutively *more* than
    twice, matching from the right.

    This stores loops exactly two times to allow inferring parent/child
    relationships correctly.

    >>> overlong_loop([1])
    False
    >>> overlong_loop([1, 1])
    True
    >>> overlong_loop([1, 1, 1])
    True
    >>> overlong_loop([1, 1, 2])
    False

    >>> overlong_loop([2, 1, 1])
    True
    >>> overlong_loop([2, 1, 1, 1])
    True
    >>> overlong_loop([2, 1, 1, 2])
    False

    >>> overlong_loop([1, 2, 3, 1, 2, 3])
    True
    >>> overlong_loop([1, 2, 3, 1, 2, 3, 4])
    False

    """
    # Check for all patterns up to path/2 length. To contain a loop two
    # times, the loop path can be at most path/2. For uneven lengths it
    # can only be path/2-1 which is what integer division in Python
    # does.
    for sub_len in xrange(1, len(path)/2+1):
        pattern = path[-sub_len:]
        candidate = path[-sub_len*2:-sub_len]
        if pattern == candidate:
            return True
    return False


def path_starts_with(path, prefix):
    """Test whether the path starts with another path.

    >>> path_starts_with([1], [1])
    True
    >>> path_starts_with([1, 2], [1])
    True
    >>> path_starts_with([2], [1])
    False
    >>> path_starts_with([1,2,3], [1,2,3])
    True
    >>> path_starts_with([1,2,3], [1,2])
    True

    >>> path_starts_with(
    ...    ('\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x01',
    ...     '\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x03',
    ...     '\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x02',
    ...     '\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x01'),
    ...    ('\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x01',
    ...     '\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x03',
    ...     '\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x02'))
    True

    """
    return path[:len(prefix)] == prefix


class StructureIndex(persistent.Persistent):
    """Stores information about the relationships between objects.

    It allows you to determine the parent-child relationship between two
    objects without having to materialize the objects in memory.

    """

    zope.interface.implements(gocept.objectquery.interfaces.IStructureIndex)

    def __init__(self, root):
        self.paths = OOBTree()
        self.insert(None, root)

    def index(self, obj):
        recursive_unindex = []
        child_paths = []
        for child in parser.get_descendants(obj):
            new_paths = self.insert(obj, child)
            loops = [path for path in new_paths if overlong_loop(path)]
            if not loops:
                recursive_unindex.extend(self.index(child))
            child_paths.extend(new_paths)

        # Remove paths not found anymore
        for path_set, path in self.paths_traversing_obj(obj):
            for candidate in child_paths:
                if path_starts_with(path, candidate):
                    # This is a valid path that is still referenced.
                    break
            else:
                # This path is not referenced anymore.
                path_set.remove(path)

        # Mark objects that have not paths anymore for unindexing
        local_unindex = []
        for candidate, path_set in self.paths.items():
            if len(path_set) > 0:
                continue
            local_unindex.append(candidate)
        # Delete buckets. XXX Maybe don't delete buckets. This might be
        # a conflict hotspot.
        for candidate in local_unindex:
            del self.paths[candidate]
        return (recursive_unindex +
                [obj._p_jar.get(candidate) for candidate in local_unindex])

    def paths_traversing_obj(self, obj):
        """List all paths that touch the given obj and traverse *past*
        it."""
        try:
            obj._p_oid
        except AttributeError:
            return
        for path_set in self.paths.values():
            for path in list(path_set):
                if obj._p_oid in path[:-1]:
                    yield path_set, path

    def insert(self, parent, child):
        # Establish a new path to child_id for each path that leads to
        # parent_id.
        try:
            child_id = child._p_oid
        except AttributeError:
            return []
        new_paths = []
        for parent_path in self.get_paths(parent):
            new_paths.append(parent_path + (child_id,))
        if not self.paths.has_key(child_id):
            self.paths[child_id] = OOTreeSet()
        for path in new_paths:
            self.paths[child_id].insert(path)
        return new_paths

    def is_child(self, child, parent):
        """ Check if key1 is a direct successor of key2. """
        if not child or not parent:
            return True   # empty keys return True (see KCJoin)
        for elem1 in self.paths.get(child, []):
            for elem2 in self.paths.get(parent):
                if len(elem1) == len(elem2) + 1 and \
                    self._check_path(elem2, elem1):
                    return True
        return False

    def is_successor(self, child, parent):
        """ Check if key1 is a successor of key2. """
        for elem1 in self.paths.get(child):
            for elem2 in self.paths.get(parent):
                if self._check_path(elem2, elem1):
                    return True
        return False

    def get_paths(self, obj):
        """Return all paths that lead to the given object."""
        if obj is None:
            # `None` is a special parent for the root object causing the
            # root path to be expressed as get_paths(None) + (root._p_oid)
            return [()]
        try:
            return self.paths[obj._p_oid]
        except KeyError:
            return []

    def _check_path(self, path1, path2):
        """ Check if path1 is reachable by path2. """
        if len(path1) > len(path2):
            return False
        for i in range(len(path1)):
            if path1[i] != path2[i]:
                return False
        return True


class MonitoringCreationDict(dict):

    def __init__(self, connection):
        self.connection = connection

    def __setitem__(self, key, value):
        super(MonitoringCreationDict, self).__setitem__(key, value)
        self.connection._oq_delayed_index.add(key)

    def update(self, data):
        super(MonitoringCreationDict, self).update(data)
        for oid in data:
            self.connection._oq_delayed_index.add(oid)


class IndexSynchronizer(object):
    """A transaction synchronizer for automatically updating the indexes on
    transaction boundaries.
    """

    zope.interface.implements(transaction.interfaces.ISynchronizer)

    def __init__(self):
        self.indexing = False

    def beforeCompletion(self, transaction):
        """Hook that is called by the transaction at the start of a commit.
        """
        if self.indexing:
            return
        for data_manager in transaction._resources:
            if not isinstance(data_manager, ZODB.Connection.Connection):
                continue
            root = data_manager.root()
            if not '_oq_collection' in root:
                return
            data_manager._oq_delayed_index = set()
            for obj in data_manager._registered_objects:
                data_manager._oq_delayed_index.add(obj._p_oid)
            data_manager._creating = MonitoringCreationDict(data_manager)

    def afterCompletion(self, txn):
        """Hook that is called by the transaction after completing a commit.
        """
        transaction.begin()
        if self.indexing:
            return
        self.indexing = True
        for data_manager in txn._resources:
            if not isinstance(data_manager, ZODB.Connection.Connection):
                continue
            root = data_manager.root()
            if not '_oq_collection' in root:
                return
            collection = root['_oq_collection']

            # Remove our class, but leave the data.
            data_manager._creating = dict(data_manager._creating)

            # Process index requests
            to_index = data_manager._oq_delayed_index
            delayed = set()
            while to_index:
                last_to_index = to_index
                for item in to_index:
                    obj = collection._p_jar.get(item)
                    try:
                        collection.index(obj)
                    except Exception:
                        # XXX too coarse
                        delayed.add(item)
                to_index = delayed
                if last_to_index == to_index:
                    # XXX This is bad.
                    break
                delayed = set()
        transaction.commit()
        self.indexing = False


    def newTransaction(self, transaction):
        """Hook that is called at the start of a transaction.
        """
        pass
