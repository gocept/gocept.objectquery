# Copyright (c) 2007 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

from gocept.objectquery.indexsupport import ClassIndex, AttributeIndex,\
    StructureIndex
from gocept.objectquery.querysupport import ObjectParser

class ObjectCollection(object):
    """ ObjectCollection provides functionallity to QueryProcessor.

        It helps to query for objects and bounds the indexes from
        IndexSupport.
    """

    def __init__(self, connection):
        """ Initialize Objectcollection. """
        # init IndexSupport
        dbroot = connection.root()
        self._classindex = ClassIndex(dbroot)
        self._attributeindex = AttributeIndex(dbroot)
        self._structureindex = StructureIndex(dbroot)
        # init QuerySupport
        self._objectparser = ObjectParser()
        self.conn = connection

    def add(self, object_oid, parent_oid=None, cycle_prev=None):
        """ Index the object to the ObjectCollection. """
        if cycle_prev is None:
            cycle_prev = []
        if object_oid in cycle_prev:
            return
        object = self.conn.get(object_oid)
        classname = self._get_classname(object)
        self._classindex.insert(classname, object_oid)
        self._objectparser.parse(object)
        for attr in self._objectparser.result("attributes"):
            self._attributeindex.insert(attr, object_oid)
        self._structureindex.insert(object_oid, parent_oid)
        descendants = self._objectparser.result("descendants")[:]
        cycle_prev.append(object_oid)
        for desc in descendants:
            self.add(desc._p_oid, object_oid, cycle_prev)

    def root(self):
        """ Return the root object. """
        return self.conn.get(self._structureindex.root())

    def by_class(self, name):
        """ Return a list of objects which match ``name``. """
        classlist = []
        for elem in self._classindex.get(name):
             classlist.append(self.conn.get(elem))
        return classlist

    def by_attr(self, name, value=None):
        """ Return a list of objects which have an attribute ``name``. """
        classlist = []
        for elem_oid in self._attributeindex.get(name):
            elem = self.conn.get(elem_oid)
            if value is None or getattr(elem, name) == value:
                classlist.append(elem)
        return classlist

    def is_child(self, key1_oid, key2_oid):
        return self._structureindex.is_child(key1_oid, key2_oid)

    def is_parent(self, key1_oid, key2_oid):
        return self._structureindex.is_parent(key1_oid, key2_oid)

    def is_successor(self, key1_oid, key2_oid):
        return self._structureindex.is_successor(key1_oid, key2_oid)

    def is_predecessor(self, key1_oid, key2_oid):
        return self._structureindex.is_predecessodecessor(key1_oid, key2_oid)

    def _get_classname(self, object):
        """ Return the classname of object. """
        if not str(type(object)).startswith("<class"):
            raise ValueError("%s is not an instantiated class." % object)
        return object.__class__.__name__

    def delete(self, object_oid, parent_oid=None, pdb=None):
        """ Main remove method. """
        if pdb is not None:
            import pdb; pdb.set_trace() 
        object = self.conn.get(object_oid)
        classname = self._get_classname(object)
        self._structureindex.delete(object_oid, parent_oid)
        if not self._structureindex.has_key(object_oid):
            self._classindex.delete(classname, object_oid)
            self._objectparser.parse(object)
            for attr in self._objectparser.result("attributes"):
                self._attributeindex.delete(attr, object_oid)
            descendants = self._objectparser.result("descendants")[:]
            for desc in descendants:
                self.delete(desc._p_oid, object_oid)
