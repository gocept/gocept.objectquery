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

    def add(self, obj_oid, parent_oid=None, cycle_prev=None):
        """ Index the object to the ObjectCollection. """
        if cycle_prev is None:
            cycle_prev = []
        if parent_oid is None and self.root():
            raise ValueError('There is already a root object present.')
        if obj_oid in cycle_prev:
            if not self._structureindex.is_successor(obj_oid, parent_oid):
                self._structureindex.insert(obj_oid, parent_oid)
            return
        op = ObjectParser()
        classname = self._get_classname(self._get_object(obj_oid))
        self._classindex.insert(classname, obj_oid)
        for attr in op.get_attributes(self._get_object(obj_oid)):
            self._attributeindex.insert(attr, obj_oid)
        self._structureindex.insert(obj_oid, parent_oid)
        cycle_prev.append(obj_oid)
        for desc in op.get_descendants(self._get_object(obj_oid)):
            self.add(desc._p_oid, obj_oid, cycle_prev[:])

    def root(self):
        """ Return the root object. """
        try:
            root = self._structureindex.root()
        except KeyError:
            return None
        return (root, root)

    def get_parents(self, elem):
        """ Return the parents for an element. """
        return self._structureindex.index['parents'][elem]

    def get_childs(self, elem):
        """ Return the childs for an element. """
        return self._structureindex.index['childs'][elem]

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

    def _get_classname(self, obj):
        """ Return the classname of object. """
        return obj.__class__.__name__

    def _get_object(self, oid):
        """ Return the object corresponding to oid. """
        return self.conn.get(oid)

    def delete(self, object_oid, parent_oid=None):
        """ Main remove method. """
        obj = self._get_object(object_oid)
        classname = self._get_classname(obj)
        op = ObjectParser()
        try:
            childs = self.get_childs(object_oid)
        except KeyError:
            childs = []
        if self._structureindex.has_key(object_oid):
            self._structureindex.delete(object_oid, parent_oid)
        if not self._structureindex.has_key(object_oid):
             self._classindex.delete(classname, object_oid)
        for attr in op.get_attributes(obj):
             self._attributeindex.delete(attr, object_oid)
        for desc in childs:
            self.delete(desc, object_oid)
