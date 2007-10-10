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
        return self._process_queryplan(qp)

    def _get_elem(self, elem):
        if not elem:                # elem is None
            return None
        elif elem[0] == "ELEM":     # elem is ("ELEM", "...")
            return self.collection.by_class(elem[1])
        elif elem[0] == "ATTR":     # elem is ["ATTR", (ID, VALUE)]
            return self.collection.by_attr(elem[1][0], elem[1][1])
        else:                       # elem is [function, ...]
            return self._process_queryplan(elem)

    def _eejoin(self, elem1, elem2):
        # get the elements
        elem1 = self._get_elem(elem1)
        elem2 = self._get_elem(elem2)
        # join elem1 and elem2
        if not elem1:       # root join
            return elem2
        else:
            result = []
            for x in elem1:
                for y in elem2:
                    if y.id == x.id: result.append(y)
        return result

    def _eajoin(self, elem1, elem2):
        # get the elements
        elem1 = self._get_elem(elem1)
        elem2 = self._get_elem(elem2)
        # join elem1 and elem2
        result = []
        for x in elem1:
            for y in elem2:
                if x == y: result.append(x)
        return result

    def _process_queryplan(self, qp):
        if qp[0] == "EEJOIN":
            result = self._eejoin(qp[1], qp[2])
        elif qp[0] == "EAJOIN":
            result = self._eajoin(qp[1], qp[2])
        return result
