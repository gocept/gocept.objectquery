# Copyright (c) 2007 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

import types

class ObjectParser(object):
    def __init__(self):
        self.attributes = []     # saves all found attributes to one object
        self.descendants = []    # saves all found descendands to one object

    def parse(self, object):
        self.__init__()
        if hasattr(object, "__dict__"):
            for x in object.__dict__.keys():
                self.attributes.append(x)
                elem = object.__dict__[x]
                if self._is_list(elem) or self._is_tuple(elem):
                    self._traverse(elem)
                elif self._is_dict(elem):
                    self._traverse(self._dict2list(elem))
                elif self._is_class(elem):
                    self.descendants.append(elem)

    def result(self, filter=None):
        if filter is not None:
            return getattr(self, filter)

    def _traverse(self, object):
        for elem in object:
            if self._is_list(elem) or self._is_tuple(elem) or\
                  self._is_dict(elem):
                self.parse(elem)
            elif self._is_class(elem):
                self.descendants.append(elem)

    def _is_list(self, object):
        if isinstance(object, types.ListType) or\
              str(type(object)).startswith("<class 'persistent"):
            return True
        return False

    def _is_tuple(self, object):
        if isinstance(object, types.TupleType):
            return True
        return False

    def _is_dict(self, object):
        if isinstance(object, types.DictType) or\
              str(type(object)).startswith("<class 'persistent"):
            return True
        return False

    def _is_class(self, object):
        classstring = str(type(object))
        if classstring.startswith("<class"):
            if classstring.startswith("<class 'persistent"):
                return False
            return True
        return False

    def _dict2list(self, dict):
        returnlist = []
        for elem in dict.values():
            if self._is_list(elem):
                returnlist.extend(elem)
            elif self._is_tuple(elem):
                returnlist.extend(list(elem))
            elif self._is_dict(elem):
                returnlist.extend(self._dict2list(elem))
            else:
                returnlist.append(elem)
        return returnlist

class EEJoin(object):
    """ Element-Element Join. """
    def __init__(self, structindex, conn=None):
        self._structindex = structindex
        self._conn = conn

    def __call__(self, elemlist1, elemlist2, direct=False, subindex=None,
                                                                  way=None):
        """ Return all elements which are (direct) childs of elem2.

            If a subindex is provided, then only thoses elements under these
            are returned.
        """
        resultlist = []
        comparer = getattr(self._structindex, "is_successor")
        if direct:
            comparer = getattr(self._structindex, "is_child")
        for elem1 in elemlist1:
            for elem2 in elemlist2:
                if elem1 not in resultlist and comparer(elem1, elem2) and\
                      (way is None or self._check_way(elem1, elem2, way)):
                    resultlist.append(elem1)
        if subindex is None:
            return resultlist
        filteredlist = []
        for elem in resultlist:
            if self._structindex.validate(elem, subindex):
                filteredlist.append(elem)
        return filteredlist

    def _check_way(self, elem1, elem2, way):
        elem1 = self._conn.get(elem1)
        elem2 = self._conn.get(elem2)
        if elem1 in getattr(elem2, way):
            return True
        return False

class EAJoin(object):
    """ Element-Attribute-Join. """
    def __call__(self, elemlist1, elemlist2):
        """ Merge the two element lists.

            elemlist1 holds all objects which match the element condition.
            elemlist2 holds all objects which match the predicate condition.
        """
        resultlist = []
        for elem1 in elemlist1:
            for elem2 in elemlist2:
                if elem1 == elem2 and elem1 not in resultlist:
                    resultlist.append(elem1)
        return resultlist

class KCJoin(object):
    """ Element-Occurence-Join. """
    def __call__(self, elemlist, occ):
        if (occ == "?" and len(elemlist) < 2):
            return elemlist
        if (occ == "+" and len(elemlist) > 0):
            return elemlist
        if (occ == "*"):
            return elemlist
        return []

class Union(object):
    """ Union of two element lists. """
    def __call__(self, elemlist1, elemlist2):
        elemlist1.extend(elemlist2)
        return elemlist1

