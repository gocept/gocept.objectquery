# Copyright (c) 2007 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

import types
from gocept.objectquery.indexsupport import PathIndex, ElementIndex

class ObjectCollection(object):
    def __init__(self):
        # define an Element- and PathIndex
        self.__element_index = ElementIndex()
        self.__path_index = {}

    def add(self, object, parent=None):
        if str(type(object)).startswith("<class"):
            if parent is None:
                self.__element_index.add(object)
                self.__path_index[object] = PathIndex()
            else:
                self.__element_index.add(object, parent)
                self.__path_index[object] = self.__path_index[parent].bear(
                                                                        object)
        # Look through objects __dict__ for classes and tupels or the like.
        if hasattr(object, "__dict__"):
            for x in object.__dict__.keys():
                # Is x a list or a tuple, then traverse it and add the
                # content.
                if isinstance(object.__dict__[x],
                              types.ListType) or isinstance(object.__dict__[x],
                                                            types.TupleType):
                    for y in object.__dict__[x]:
                        self.add(y, object)
                # Is x a dictionary, then traverse it and add the content.
                elif isinstance(object.__dict__[x], types.DictType):
                    for y in object.__dict__[x].keys():
                        self.add(object.__dict__[x][y], object)
                # Is x another class, then add it.
                elif str(type(object.__dict__[x])).startswith("<class"):
                    self.add(object.__dict__[x], object)

    def __unindex(self, object, parent=None):
        remlist = self.__element_index.list(object)
        for elem in remlist:
            self.__unindex(elem, object)
        del self.__path_index[object]

    def remove(self, object, parent=None):
        self.__unindex(object, parent)
        self.__element_index.delete(object, parent)

    def root(self):
        return self.__element_index.root()

    def all(self):
        return self.__element_index.rlist()

    def by_class(self, name, pathindex=None):
        if pathindex is None:
            pathindex = self.__path_index[self.root()]
        return [e for e in self.all() if (e.__class__.__name__ == name) and \
                                (self.__path_index[e] in pathindex)]

    def by_attr(self, id, value):
        return [elem for elem in self.all() if hasattr(elem, id) and \
                                (getattr(elem, id) == value)]


    def debug(self):
        print self.__element_index.rlist()
        print self.__path_index
