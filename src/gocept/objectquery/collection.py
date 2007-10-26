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
        self.__counter = {}

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
        if self.__counter.get(object, None) is None:
            self.__counter[object] = 0
        self.__counter[object] = self.__counter[object] + 1

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

    def move(self, object, parent, target):
        self.__element_index.move(object, parent, target)
        movelist = []
        for child in self.__path_index[object]:
            for par in self.__path_index[parent]:
                if child in par:
                    movelist.append((par, child))
        for child in movelist:
            for newpar in self.__path_index[target]:
                child[0].move(child[1], newpar)

    def root(self):
        return self.__element_index.root()

    def all(self):
        return self.__element_index.rlist()

    def __check_path_index(self, pi_child_list, pi_parent_list):
        for child in pi_child_list:
            for parent in pi_parent_list:
                if child in parent:
                    return True
        return False

    def by_class(self, name, pathindex=None):
        if pathindex is None:
            pathindex = self.__path_index[self.root()]
        return [e for e in self.all() if (e.__class__.__name__ == name) and \
                    self.__check_path_index(self.__path_index.get(e, []),
                                            pathindex)]

    def by_attr(self, id, value):
        return [elem for elem in self.all() if hasattr(elem, id) and \
                                (getattr(elem, id) == value)]

    def get_namespace(self, object=None):
        if object is None:
            object = self.root()
        return self.__path_index[object]

    def is_direct_child(self, child, parent, pi=None):
        if pi is None:
            pi = self.__path_index[parent]
        if child in self.__element_index.list(parent):
            for cpi in self.__path_index[child]:
                for ppi in pi:
                    if cpi in ppi:
                        return True
        return False

    def debug(self):
        i = 0
        for elem in self.__element_index.rlist():
            print str(i) + ": " + str(elem)
            print self.__path_index[elem]
            i = i + 1
