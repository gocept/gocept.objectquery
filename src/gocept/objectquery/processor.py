# Copyright (c) 2007 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

import gocept.objectquery.resultset

class QueryProcessor(object):
    """ Processes a query to the collection and returns the results.

    QueryProcessor parses a query with the given parser. It returns a
    resultset object with the results from the given collection.
    """

    def __init__(self, parser, collection):
        self.collection = collection
        self.parser = parser
        self.resultset = gocept.objectquery.resultset.ResultSet()

    def __call__(self, expression):
        qp = self.parser.parse(expression)
        return self._process_queryplan(qp,(1,100))

    def _get_elem(self, elem, ns):
        if not elem:                # elem is None
            return None
        elif elem[0] == "ELEM":     # elem is ("ELEM", "...")
            return self.collection.by_class(elem[1], ns)
        elif elem[0] == "ATTR":     # elem is ["ATTR", (ID, VALUE)]
            return self.collection.by_attr(elem[1][0], elem[1][1])
        else:                       # elem is [function, ...]
            return self._process_queryplan(elem, ns)

    def _eejoin(self, elem1, elem2, ns):
        # get the elements
        elem1 = self._get_elem(elem1, ns)
        if not elem1:       # root join
            return elem2
        else:
            result = []
            for par in elem1:
                desc = self._get_elem(elem2, par.__ns__)
                # join par (parent) and desc (descendant)
                #for d in desc:
                #    p_order, p_size = par.__ns__
                #    d_order, d_size = d.__ns__
                #    if d_order > p_order and d_order < (p_order + p_size):
                #        result.append(d)
                result.extend(desc)
        return result

    def _eajoin(self, elem1, elem2, ns):
        # get the elements
        elem1 = self._get_elem(elem1, ns)
        elem2 = self._get_elem(elem2, ns)
        # join elem1 and elem2
        result = []
        for x in elem1:
            for y in elem2:
                if x == y: result.append(x)
        return result

    def _kcjoin(self, occ, elem, ns):
        # get the elements
        elem = self._get_elem(elem, ns)
        # grouping
        # bla = []
        #for x in elem:
        #    f = 0
        #    for y in bla:
        #        if x.__parent__ == y: f = 1
        #    if f == 0:
        #        bla.append(x.__parent__)
        #elemn = []
        #for x in bla:
        #    elemn.append(x)
        #    elemn[x] = []
        #    for y in elem:
        #        if y.__parent__ == x: elemn[x].append(y)
        # do kcjoin
        if (occ == "?" and len(elem) < 2):
            return elem
        elif (occ == "+" and len(elem) > 0):
            return elem
        elif (occ == "*"):
            return elem
        return []

    def _process_queryplan(self, qp, ns):
        if qp[0] == "EEJOIN":
            result = self._eejoin(qp[1], qp[2], ns)
        elif qp[0] == "EAJOIN":
            result = self._eajoin(qp[1], qp[2], ns)
        elif qp[0] == "KCJOIN":
            result = self._kcjoin(qp[1], qp[2], ns)
        return result
