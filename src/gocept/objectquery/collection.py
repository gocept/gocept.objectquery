# Copyright (c) 2007 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

from gocept.objectquery.indexsupport import ClassIndex, AttributeIndex,\
    StructureIndex
from gocept.objectquery.querysupport import ObjectParser, EEJoin, EAJoin,\
    KCJoin, Union

class ObjectCollection(object):
    """ ObjectCollection provides functionallity to QueryProcessor.

        It helps to query for objects and bounds the indexes from
        IndexSupport.
    """

    def __init__(self, connection):
        """ Initialize ObjectCollection. """
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
        # init AttributeComparison
        self.comp_map = {
            "==": lambda x, y: x == y,
            "<": lambda x, y: float(x) < float(y),
            "<=": lambda x, y: float(x) <= float(y),
            ">": lambda x, y: float(x) > float(y),
            ">=": lambda x, y: float(x) >= float(y),
            "!=": lambda x, y: x != y }

    def add(self, object_oid, parent_oid=None, cycle_prev=None):
        """ Index the object to the ObjectCollection. """
        if cycle_prev is None:
            cycle_prev = []
        if object_oid in cycle_prev:
            return
        object = self._get_object(object_oid)
        classname = self._get_classname(object)
        self._classindex.insert(classname, object_oid)
        self._objectparser.parse(object)
        for attr in self._objectparser.result("attributes"):
            self._attributeindex.insert(attr, object_oid)
        self._structureindex.insert(object_oid, parent_oid)
        descendants = self._objectparser.result("descendants")[:]
        cycle_prev.append(object_oid)
        for desc in descendants:
            self.add(self._get_oid(desc), object_oid, cycle_prev[:])

    def root(self):
        """ Return the root object. """
        return self._structureindex.root()

    def all(self):
        """ Return all objects. """
        return self._classindex.all()

    def by_class(self, name):
        """ Return a list of objects which match ``name``. """
        return self._classindex.get(name)

    def _attr_comp(self, attr, value, comp_op):
        if comp_op is None or comp_op == '=':
            comp_op = '=='
        return self.comp_map[comp_op](attr, value)

    def by_attr(self, name, value=None, comp_op=None):
        """ Return a list of objects which have an attribute ``name``. """
        classlist = []
        for elem_oid in self._attributeindex.get(name):
            elem = self._get_object(elem_oid)
            if value is None or self._attr_comp(getattr(elem, name), value,
                                                                    comp_op):
                classlist.append(elem_oid)
        return classlist

    def is_child(self, key1_oid, key2_oid):
        return self._structureindex.is_child(key1_oid, key2_oid)

    def is_successor(self, key1_oid, key2_oid):
        return self._structureindex.is_successor(key1_oid, key2_oid)

    def eejoin(self, *args):
        return self._eejoin(*args)

    def eajoin(self, *args):
        return self._eajoin(*args)

    def kcjoin(self, elemlist, occ):
        return self._kcjoin(elemlist, occ)

    def union(self, elemlist1, elemlist2):
        return self._union(elemlist1, elemlist2)

    def _get_classname(self, object):
        """ Return the classname of object. """
        if not str(type(object)).startswith("<class"):
            raise ValueError("%s is not an instantiated class." % object)
        return object.__class__.__name__

    def _get_oid(self, object):
        """ Return the oid of object. """
        return object._p_oid

    def _get_object(self, oid):
        """ Return the object corresponding to oid. """
        return self.conn.get(oid)

    def get_structureindex(self, key=None):
        """ Return the StructureIndex for a given key (or the root). """
        if key is None:
             key = self._structureindex.root()
        return self._structureindex.get(key)

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
