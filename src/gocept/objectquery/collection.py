# Copyright (c) 2007-2008 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

from gocept.objectquery.indexsupport import ClassIndex, AttributeIndex,\
    StructureIndex
from gocept.objectquery.querysupport import ObjectParser, EEJoin, EAJoin,\
    KCJoin, Union
from zope.interface import implements
from gocept.objectquery.interfaces import IObjectCollection


class ObjectCollection(object):
    """ObjectCollection provides functionality to QueryProcessor.

    It helps to query for objects and bounds the indexes from
    IndexSupport.
    """

    implements(IObjectCollection)

    def __init__(self, connection):
        self.conn = connection
        dbroot = self.conn.root()
        # init IndexSupport
        self._classindex = ClassIndex(dbroot)
        self._attributeindex = AttributeIndex(dbroot)
        self._structureindex = StructureIndex(dbroot)
        # init QuerySupport
        self._eejoin = EEJoin(self._structureindex)
        self._eajoin = EAJoin(self.conn) # XXX: ValueIndex instead of conn
        self._kcjoin = KCJoin(self._structureindex)
        self._union = Union()

    def add(self, obj, parent=None, cycle_prev=None):
        """ Index the object to the ObjectCollection. """
        if not hasattr(obj, '_p_oid'):
            return
        if cycle_prev is None:
            cycle_prev = []
        parent_oid = None
        if parent:
            parent_oid = parent._p_oid
        if obj._p_oid in cycle_prev:
            if not self._structureindex.is_successor(obj._p_oid, parent_oid):
                self._structureindex.insert(obj._p_oid, parent_oid)
            return
        op = ObjectParser()
        classname = self._get_classname(obj)
        self._classindex.insert(classname, obj._p_oid)
        for attr in op.get_attributes(obj):
            self._attributeindex.insert(attr, obj._p_oid)
        self._structureindex.insert(obj._p_oid, parent_oid)
        cycle_prev.append(obj._p_oid)
        for desc in op.get_descendants(obj):
            self.add(desc, obj, cycle_prev[:])

    def root(self):
        """ Return the root object. """
        root = self._structureindex.root()
        return (root, root)

    def all(self):
        """ Return all objects. """
        return [ (elem, elem) for elem in self._classindex.all() ]

    def by_class(self, name):
        """ Return a list of objects which match ``name``. """
        return [ (elem, elem) for elem in self._classindex.get(name) ]

    def is_child(self, *args):
        return self._structureindex.is_child(*args)

    def eejoin(self, *args):
        return self._eejoin(*args)

    def eajoin(self, *args):
        return self._eajoin(*args)

    def kcjoin(self, *args):
        return self._kcjoin(*args)

    def union(self, *args):
        return self._union(*args)

    def _get_classname(self, object):
        """ Return the classname of object. """
        return object.__class__.__name__

    def _get_object(self, oid):
        """ Return the object corresponding to oid. """
        return self.conn.get(oid)

    def delete(self, object_oid, parent_oid=None, pdb=None):
        """ Main remove method. """
        obj = self._get_object(object_oid)
        classname = self._get_classname(obj)
        op = ObjectParser()
        if self._structureindex.has_key(object_oid):
            self._structureindex.delete(object_oid, parent_oid)
        if not self._structureindex.has_key(object_oid):
             self._classindex.delete(classname, object_oid)
        for attr in op.get_attributes(obj):
             self._attributeindex.delete(attr, object_oid)
        for desc in op.get_descendants(obj):
            self.delete(desc._p_oid, object_oid)
