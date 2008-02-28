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
        self._eajoin = EAJoin()
        self._kcjoin = KCJoin()
        self._union = Union()

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

    def by_class(self, name, si=None):
        """ Return a list of objects which match ``name``. """
        classlist = []
        for elem in self._classindex.get(name):
            if si is None or self._structureindex.validate(elem, si):
                classlist.append(elem)
        return classlist

    def by_attr(self, name, value=None):
        """ Return a list of objects which have an attribute ``name``. """
        classlist = []
        for elem_oid in self._attributeindex.get(name):
            elem = self._get_object(elem_oid)
            if value is None or getattr(elem, name) == value:
                classlist.append(elem_oid)
        return classlist

    def is_child(self, key1_oid, key2_oid):
        return self._structureindex.is_child(key1_oid, key2_oid)

    def is_successor(self, key1_oid, key2_oid):
        return self._structureindex.is_successor(key1_oid, key2_oid)

    def eejoin(self, elemlist1, elemlist2, direct=False, subindex=None):
        return self._eejoin(elemlist1, elemlist2, direct, subindex)

    def eajoin(self, elemlist1, elemlist2):
        return self._eajoin(elemlist1, elemlist2)

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
