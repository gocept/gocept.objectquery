# Copyright (c) 2007-2008 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

import persistent
from gocept.objectquery.indexsupport import ClassIndex, AttributeIndex,\
    StructureIndex
from gocept.objectquery.querysupport import EEJoin, EAJoin,\
    KCJoin, Union
from zope.interface import implements
from gocept.objectquery.interfaces import IObjectCollection


class ObjectCollection(persistent.Persistent):
    """ObjectCollection provides functionality to QueryProcessor.

    It helps to query for objects and bounds the indexes from
    IndexSupport.

    """

    implements(IObjectCollection)

    def __init__(self, connection):
        self.root = connection.root()
        self.class_index = ClassIndex()
        self.attribute_index = AttributeIndex()
        self.structure_index = StructureIndex(self.root)

    def index(self, obj):
        if obj in [self, self.class_index, self.structure_index,
                self.attribute_index]:
            return
        self.class_index.index(obj)
        self.attribute_index.index(obj)
        unindex = self.structure_index.index(obj)
        for obj in unindex:
            self.class_index.unindex(obj)
            self.attribute_index.unindex(obj)

    def get_parents(self, elem):
        """ Return the parents for an element. """
        return self.structure_index.index['parents'][elem]

    def get_childs(self, elem):
        """ Return the childs for an element. """
        return self._structureindex.index['childs'][elem]

    def all(self):
        """ Return all objects. """
        return [ (elem, elem) for elem in self.class_index.all() ]

    def by_class(self, class_):
        """ Return a list of objects which match ``name``. """
        return [(elem, elem) for elem in self.class_index.query(class_)]

    def is_child(self, *args):
        return self.structure_index.is_child(*args)

    def eejoin(self, *args):
        join = EEJoin(self.structure_index)
        return join(*args)

    def eajoin(self, *args):
        self._eajoin = EAJoin(self._p_jar) # XXX: ValueIndex instead of conn
        return self._eajoin(*args)

    def kcjoin(self, *args):
        self._kcjoin = KCJoin(self.structure_index)
        return self._kcjoin(*args)

    def union(self, *args):
        return self._union(*args)
        self._union = Union()
