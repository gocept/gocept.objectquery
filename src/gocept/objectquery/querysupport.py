# Copyright (c) 2007-2008 gocept gmbh & co. kg
# See also LICENSE.txt


def normalize_range_tuples(list):
    """Expand single elements into (element, element) pairs."""
    for i, v in enumerate(list):
        if not isinstance(v, tuple):
            v = (v, v)
        list[i] = v


class EEJoin(object):
    """ Element-Element Join. """

    def __init__(self, structindex):
        self._structindex = structindex

    def __call__(self, E, F, kcwild=None):
        """ Returns a set of (e, f) pairs such that e is an ancestor f. """
        normalize_range_tuples(E)
        normalize_range_tuples(F)

        resultlist = []
        comparer = getattr(self._structindex, "is_child")
        if kcwild is not None:
            comparer = getattr(self._structindex, "is_successor")
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
            "<": lambda x, y: x < y,
            "<=": lambda x, y: x <= y,
            ">": lambda x, y: x > y,
            ">=": lambda x, y: x >= y,
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
        # XXX: ToDo use a ValueIndex instead of unpickling the obj
        # for retrieving its attribute values (#5779)
        for e in E:
            elem = e[1]
            if self.conn is not None:
                elem = self.conn.get(elem)
            if not hasattr(elem, attrname):
                continue
            if e in resultlist:
                continue
            if attrvalue is None:
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
        normalize_range_tuples(elemlist)
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
