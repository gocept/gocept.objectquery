# Copyright (c) 2007 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

MAX_CHILD = 10
MAX_HEIGHT = 5

class RootObject:
    pass

class ObjectCollection:
    """ Holds objects and provides functionality on them. """
    def __init__(self):
        """ initialize the collection """
        root = RootObject()
        self.collection = [root]
        self._namespace = {root: (1, MAX_CHILD**MAX_HEIGHT-1)}
        self._eeindex = {root: []}

    def _get_new_namespace(self, object):
        namespace = self._namespace.get(object, self.collection[0])
        sons = len(self._eeindex.get(object, self.collection[0]))
        if sons >= MAX_CHILD:
            raise ValueError("Maximum number of childs exeeded (%i)"
                             % MAX_CHILD)
        block_value = namespace[1] / MAX_CHILD
        order_value = namespace[0] + 1 + (block_value * sons)
        size_value = block_value - 1
        return (order_value, size_value)

    def index(self, object):
        self.add(object, self.collection[0])

    def add(self, object, parent):
        if self._namespace.get(object, None) is not None:
            raise ValueError("%s already exists in collection" % object)
        if str(type(object))[0:6] == "<class":
            self._namespace[object] = self._get_new_namespace(parent)
            self._eeindex[parent].append(object)
            self._eeindex[object]= []
            self.collection.append(object)
        if hasattr(object, "__dict__"):
            for x in object.__dict__.keys():
                if str(type(object.__dict__[x])) == "<type 'list'>":
                    for y in object.__dict__[x]:
                        self.add(y, object)
                elif str(type(object.__dict__[x])) == "<type 'dict'>":
                    for y in object.__dict__[x].keys():
                        self.add(object.__dict__[x][y], object)
                elif str(type(object.__dict__[x]))[0:6] == "<class":
                    self.add(object.__dict__[x], object)

    def all(self):
        return self.collection[1:]  # suppress the RootObject

    def root(self):
        return [ self.collection[0] ]

    def by_class(self, name, namespace=None):
        if namespace is None:
            namespace = self._namespace.get(self.collection[0])
        return [ elem for elem in self.collection
                        if elem.__class__.__name__ == name
                        and self._namespace.get(elem)[0] >= namespace[0]
                        and self._namespace.get(elem)[0] <= (namespace[0] +
                                                             namespace[1])
               ]

    def by_attr(self, id, value):
        return [ elem for elem in self.collection
                        if hasattr(elem, id) and (getattr(elem, id) == value) ]

    def is_direct_child(self, child, parent):
        for elem in self._eeindex.get(parent):
            if elem == child:
                return True
        return False

    def get_value(self, id):
        return [ getattr(elem, id) for elem in self.collection
                        if hasattr(elem, id) ]

    def get_namespace(self, object):
        return self._namespace.get(object,
                                   self._namespace.get(self.collection[0]))
