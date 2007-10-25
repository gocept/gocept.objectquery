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

    def __get_descendant_objects(self, object):
        returnlist = []
        # Look through objects __dict__ for classes and tupels or the like.
        if hasattr(object, "__dict__"):
            for x in object.__dict__.keys():
                # Is x a list or a tuple, then traverse it and add the
                # content.
                if isinstance(object.__dict__[x],
                              types.ListType) or isinstance(object.__dict__[x],
                                                            types.TupleType):
                    for y in object.__dict__[x]:
                        returnlist.append(y)
                # Is x a dictionary, then traverse it and add the content.
                elif isinstance(object.__dict__[x], types.DictType):
                    for y in object.__dict__[x].keys():
                        returnlist.append(y)
                # Is x another class, then add it.
                elif str(type(object.__dict__[x])).startswith("<class"):
                    returnlist.append(object.__dict__[x])
        return returnlist

    def __add_object(self, object, parent):
        if self.__path_index.get(object, None) is None:
            self.__path_index[object] = []
        if parent is None:
            self.__element_index.add(object)
            self.__path_index[object].append(PathIndex())
        else:
            self.__element_index.add(object, parent)
            for par in self.__path_index[parent]:
                self.__path_index[object].append(par.bear(object))

    def add(self, object, parent=None):
        desclist = self.__get_descendant_objects(object)
        if str(type(object)).startswith("<class"):
            self.__add_object(object, parent)
        for elem in desclist:
            if elem not in self.__element_index.list(object):
                self.add(elem, object)
            elif len([e for e in desclist if e == elem]) !=\
                    len([e for e in self.__element_index.list(object)\
                         if e == elem]):
                self.__add_object(elem, object)

    def __unindex(self, object, parent=None):
        if parent is None:
            parent = self.root()
        childs = self.__element_index.list(object)[:]
        for elem in childs:
            self.__unindex(elem, object)
        if self.__path_index.get(parent, None) is not None:
            for pi in self.__path_index[parent]:
                if self.__path_index.get(object, None) is not None:
                    objlist = self.__path_index[object][:]
                    for obj in objlist:
                        if pi.is_direct_parent(obj):
                            pi.delete(obj)
                            self.__path_index[object].remove(obj)
                    if self.__path_index[object] == []:
                        del self.__path_index[object]

    def remove(self, object, parent=None):
        self.__unindex(object, parent)
        self.__element_index.delete(object, parent)

    def root(self):
        return self.__element_index.root()

    def all(self):
        return self.__element_index.rlist()

    def __check_path_index(self, pilist, pi):
        for p in pilist:
            if p in pi:
                return True
        return False

    def by_class(self, name, pathindex=None):
        if pathindex is None:
            pathindex = self.__path_index[self.root()][0]
        return [e for e in self.all() if (e.__class__.__name__ == name) and \
                    self.__check_path_index(self.__path_index[e], pathindex)]

    def by_attr(self, id, value):
        return [elem for elem in self.all() if hasattr(elem, id) and \
                                (getattr(elem, id) == value)]


    def debug(self):
        print self.__element_index.rlist()
        print self.__path_index
