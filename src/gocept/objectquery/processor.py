# Copyright (c) 2007 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

from gocept.objectquery.resultset import ResultSet

class QueryProcessor(object):
    """ Processes a query to the collection and returns the results.

    QueryProcessor parses a query with the given parser. It returns a
    resultset object with the results from the given collection.
    """

    def __init__(self, parser, collection):
        self.collection = collection
        self.parser = parser
        self.resultset = ResultSet()

    def __call__(self, expression):
        """ Process expression and return a queryplan. """
        qp = self.parser.parse(expression)
        pathindex = self.collection.get_pathindex()
        return self._process_queryplan(qp, pathindex)

    def __remove_multi_items(self, list):
        """ Removes multi occurences of items in a list (but keeps one). """
        mydict = {} # uses a dicts keys
        for elem in list:
            mydict[elem] = ""
        return [elem[0] for elem in mydict.items()]


    def _eajoin(self, elem1, elem2, pathindex):
        """ Element-Attribute-Join. """
        elem1 = self._get_elem(elem1, pathindex)
        elem2 = self._get_elem(elem2, pathindex)
        # join elem1 and elem2
        result = []
        for x in elem1:
            for y in elem2:
                if x == y: result.append(x)
        return result

    def _eejoin(self, elem1, elem2, pathindex):
        """ Element-Element-Join. """
        # get the parent elements
        elem1 = self._get_elem(elem1, pathindex)
        if not elem1: # root join
            elem1 = [ self.collection.root() ]
        result = []
        for par in elem1:
            desc = self._get_elem(elem2, self.collection.get_pathindex(par))
            desc = self.__remove_multi_items(desc) # bugfix
            result.extend([elem for elem in desc
                           if self.collection.is_direct_child(elem, par,
                                        self.collection.get_pathindex(par))])
        return result

    def _get_elem(self, elem, pathindex):
        """ Decide what to do with elem. """
        if not elem:                # elem is None
            return None
        elif elem[0] == "ELEM":     # elem is ("ELEM", "...")
            return self.collection.by_class(elem[1], pathindex)
        elif elem[0] == "WILDCARD": # elem is ("WILDCARD", "_")
            return self.collection.all()
        elif elem[0] == "ATTR":     # elem is ["ATTR", (ID, VALUE)]
            return self.collection.by_attr(elem[1][0], elem[1][1])
        else:                       # elem is [function, ...]
            return self._process_queryplan(elem, pathindex)

    def _kcjoin(self, occ, elem, pathindex):
        """ Element-Occurence-Join. """
        elem = self._get_elem(elem, pathindex)
        if (occ == "?" and len(elem) < 2):
            return elem
        elif (occ == "+" and len(elem) > 0):
            return elem
        elif (occ == "*"):
            return elem
        return []

    def _process_queryplan(self, qp, pathindex):
        """ Recursive process of query plan ``qp``. """
        if qp[0] == "EEJOIN":
            result = self._eejoin(qp[1], qp[2], pathindex)
        elif qp[0] == "EAJOIN":
            result = self._eajoin(qp[1], qp[2], pathindex)
        elif qp[0] == "KCJOIN":
            result = self._kcjoin(qp[1], qp[2], pathindex)
        elif qp[0] == "UNION":
            result = self._union(qp[1], qp[2], pathindex)
        return result

    def _union(self, elem1, elem2, pathindex):
        """ Union if two results. """
        elem1 = self._get_elem(elem1, pathindex)
        elem1.extend(self._get_elem(elem2, pathindex))
        return elem1
