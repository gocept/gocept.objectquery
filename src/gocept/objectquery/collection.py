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
        self._objectparser = ObjectParser()
        self._eejoin = EEJoin(self._structureindex)
        self._eajoin = EAJoin(self.conn) # XXX: ValueIndex instead of conn
        self._kcjoin = KCJoin(self._structureindex)
        self._union = Union()

    def add(self, obj, parent_oid=None, cycle_prev=None):
        """ Index the object to the ObjectCollection. """
        if cycle_prev is None:
            cycle_prev = []
        if obj._p_oid in cycle_prev:
            return
        classname = self._get_classname(obj)
        self._classindex.insert(classname, obj._p_oid)
        self._objectparser.parse(obj)
        for attr in self._objectparser.result("attributes"):
            self._attributeindex.insert(attr, obj._p_oid)
        self._structureindex.insert(obj._p_oid, parent_oid)
        descendants = self._objectparser.result("descendants")[:]
        cycle_prev.append(obj._p_oid)
        for desc in descendants:
            self.add(desc, obj._p_oid, cycle_prev[:])

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

    def _get_oid(self, object):
        """ Return the oid of object. """
        return object._p_oid

    def _get_object(self, oid):
        """ Return the object corresponding to oid. """
        return self.conn.get(oid)

    def delete(self, object_oid, parent_oid=None):
        """ Main remove method. """
        object = self._get_object(object_oid)
        classname = self._get_classname(object)
        self._structureindex.delete(object_oid, parent_oid)
        if not self._structureindex.has_key(object_oid):
            self._classindex.delete(classname, object_oid)
            self._objectparser.parse(object)
            for attr in self._objectparser.result("attributes"):
                self._attributeindex.delete(attr, object_oid)
            descendants = self._objectparser.result("descendants")[:]
            for desc in descendants:
                self.delete(self._get_oid(desc), object_oid)
