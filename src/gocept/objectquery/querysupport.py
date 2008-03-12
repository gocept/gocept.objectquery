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
    def __init__(self, structindex):
        self._structindex = structindex

    def __call__(self, E, F):
        """ Returns a set of (e, f) pairs such that e is an ancestor f. """
        resultlist = []
        comparer = getattr(self._structindex, "is_child")
        for e in E:
            for f in F:
                if f[0] is None and f[1] is None and e not in resultlist:
                    resultlist.append(e)
                    continue
                relation = (e[0], f[1])
                if relation not in resultlist and comparer(f[0], e[1]):
                    resultlist.append(relation)
        return resultlist

class EAJoin(object):
    """ Element-Attribute-Join. """
    def __init__(self, connection=None):
        self.conn = connection
        self.comp_map = {
            "==": lambda x, y: x == y,
            "<": lambda x, y: float(x) < float(y),
            "<=": lambda x, y: float(x) <= float(y),
            ">": lambda x, y: float(x) > float(y),
            ">=": lambda x, y: float(x) >= float(y),
            "!=": lambda x, y: x != y }

    def _attr_comp(self, attr, value, comp_op):
        if comp_op is None or comp_op == '=':
            comp_op = '=='
        return self.comp_map[comp_op](attr, value)

    def __call__(self, E, attrname, attrvalue=None, attrcomp=None):
        """ Returns a list of elements with attribute attrname.

        attrname is compared against attrvalue with compare operator attrcomp.
        """
        resultlist = []
        # XXX: ToDo use ValueIndex instead of connection
        for e in E:
            elem = e[1]
            if self.conn is not None:
                elem = self.conn.get(elem)
            if not hasattr(elem, attrname):
                continue
            if e in resultlist:
                continue
            if not attrvalue:
                resultlist.append(e)
                continue
            if self._attr_comp(getattr(elem, attrname), attrvalue, attrcomp):
                resultlist.append(e)
        return resultlist

class KCJoin(object):
    """ Return the Kleene Closure of elemlist. """
    def __init__(self, structindex):
        self.eejoin = EEJoin(structindex)

    def __call__(self, elemlist, occ):
        kc = []
        kc.append(elemlist)
        while kc[-1] != []:
            kc.append(self.eejoin(kc[-1], elemlist))
        paths = []
        for elem in kc:
            paths.extend(elem)
        # if occurence == ? remove all paths longer than 1
        if occ == "?":
            for elem in paths[:]:
                if elem[0] != elem[1]:
                    paths.remove(elem)
        # add a ``None-Tuple'' to allow EEJoins without delivered elems
        if occ == "?" or occ == "*":
            paths.append((None, None))
        return paths

class Union(object):
    """ Union of two element lists. """
    def __call__(self, elemlist1, elemlist2):
        elemlist1.extend(elemlist2)
        return elemlist1
