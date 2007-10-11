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
        namespace = self.collection.get_namespace(None)
        return self._process_queryplan(qp, namespace)

    def _get_elem(self, elem, namespace):
        if not elem:                # elem is None
            return None
        elif elem[0] == "ELEM":     # elem is ("ELEM", "...")
            return self.collection.by_class(elem[1], namespace)
        elif elem[0] == "ATTR":     # elem is ["ATTR", (ID, VALUE)]
            return self.collection.by_attr(elem[1][0], elem[1][1])
        else:                       # elem is [function, ...]
            return self._process_queryplan(elem, namespace)

    def _eejoin(self, elem1, elem2, namespace):
        # get the elements
        elem1 = self._get_elem(elem1, namespace)
        if not elem1:       # root join
            return elem2
        else:
            result = []
            for par in elem1:
                desc = self._get_elem(elem2,
                                      self.collection.get_namespace(par))
                result.extend(desc)
        return result

    def _eajoin(self, elem1, elem2, namespace):
        # get the elements
        elem1 = self._get_elem(elem1, namespace)
        elem2 = self._get_elem(elem2, namespace)
        # join elem1 and elem2
        result = []
        for x in elem1:
            for y in elem2:
                if x == y: result.append(x)
        return result

    def _kcjoin(self, occ, elem, namespace):
        # get the elements
        elem = self._get_elem(elem, namespace)
        if (occ == "?" and len(elem) < 2):
            return elem
        elif (occ == "+" and len(elem) > 0):
            return elem
        elif (occ == "*"):
            return elem
        return []

    def _process_queryplan(self, qp, namespace):
        if qp[0] == "EEJOIN":
            result = self._eejoin(qp[1], qp[2], namespace)
        elif qp[0] == "EAJOIN":
            result = self._eajoin(qp[1], qp[2], namespace)
        elif qp[0] == "KCJOIN":
            result = self._kcjoin(qp[1], qp[2], namespace)
        return result
