# Copyright (c) 2007 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

import types

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
        self._namespace = {root: [(1, MAX_CHILD**MAX_HEIGHT-1)]}
        self._eeindex = {root: []}
        self._eenumber = {root: 1}

    def _get_sons(self, object, pns):
        sons = []
        for elem in self._eeindex.get(object, self.collection[0]):
            if elem not in sons:
                for ons in self._namespace[elem]:
                    if ons[0] >= pns[0] and ons[0] <= (pns[0] + pns[1]):
                        sons.append(elem)
        return sons

    def _get_new_namespace(self, object):
        newns = []
        nslist = self._namespace.get(object, self.collection[0])
        oldsons = 0
        maxsons = 0
        update = False
        for namespace in nslist:
            sons = len(self._get_sons(object, namespace))
            if sons < oldsons:
                update = True
            if sons > maxsons:
                maxsons = sons
            oldsons = sons

        for namespace in nslist:
            sons = len(self._get_sons(object, namespace))
            if sons >= MAX_CHILD:
                raise ValueError("Maximum number of childs exeeded (%i)"
                                 % MAX_CHILD)
            elif not update or sons < maxsons:
                block_value = namespace[1] / MAX_CHILD
                order_value = namespace[0] + 1 + (block_value * sons)
                size_value = block_value - 1
                newns.append( (order_value, size_value) )
        return newns

    def index(self, object):
        #import pdb; pdb.set_trace() 
        self.add(object, self.collection[0], first=True)

    def add(self, object, parent, first=False):
        if str(type(object)).startswith("<class"):
            if self._namespace.get(object, None) is None:
                self._namespace[object] = []
            newns = self._get_new_namespace(parent)
            if first == True:
                newns = [ newns[-1] ]
            self._namespace[object].extend(newns)
            self._eeindex[parent].append(object)
            if self._eenumber.get(object, None) is None:
                self._eenumber[object] = 0
            self._eenumber[object] = self._eenumber[object] + len(newns)
            if self._eeindex.get(object, None) is None:
                self._eeindex[object] = []
            if not object in self.collection:
                self.collection.append(object)
        if hasattr(object, "__dict__"):
            for x in object.__dict__.keys():
                if isinstance(object.__dict__[x],
                              types.ListType) or isinstance(object.__dict__[x],
                                                            types.TupleType):
                    for y in object.__dict__[x]:
                        self.add(y, object, first)
                elif isinstance(object.__dict__[x], types.DictType):
                    for y in object.__dict__[x].keys():
                        self.add(object.__dict__[x][y], object, first)
                elif str(type(object.__dict__[x])).startswith("<class"):
                    self.add(object.__dict__[x], object, first)

    def remove(self, object, parent):
        parentlist = [ elem for elem in self._eeindex[parent] if elem ==
                      object ]
        for elem in parentlist:
            self.unindex(elem, parent)
            self._eeindex[parent].remove(elem)

    def unindex(self, object, parent):
        if self._eeindex.get(object, None) is not None:
            for elem in [ bla for bla in self._eeindex[object] ]:
                self.unindex(elem, object)
            for pns in self._namespace[parent]:
                for ons in self._namespace[object]:
                    if ons[0] >= pns[0] and ons[0] <= (pns[0] + pns[1]):
                        self._namespace[object].remove(ons)
                        self._eenumber[object] = self._eenumber[object] - 1
            if self._eenumber[object] <= 0:
                del self._namespace[object]
                self.collection.remove(object)
                del self._eenumber[object]
                del self._eeindex[object]

    def all(self):
        return self.collection[1:]  # suppress the RootObject

    def root(self):
        return [ self.collection[0] ]

    def _is_parent(self, nslist, parent):
        for ons in nslist:
            if ons[0] >= parent[0] and ons[0] <= (parent[0] + parent[1]):
                return True
        return False

    def by_class(self, name, namespace=None):
        if namespace is None:
            namespace = self._namespace.get(self.collection[0])
        returnlist = []
        for ns in namespace:
            returnlist.extend([ elem for elem in self.collection
                        if elem.__class__.__name__ == name
                        and self._is_parent(self._namespace.get(elem), ns)])
        return returnlist

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
