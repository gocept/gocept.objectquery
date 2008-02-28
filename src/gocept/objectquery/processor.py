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

    def __call__(self, expression, pdb=None):
        """ Process expression and return a queryplan. """
        if pdb:
            import pdb; pdb.set_trace() 
        qp = self.parser.parse(expression)
        result = self._process_queryplan(qp)
        return self._oids2objects(result)

    def _oids2objects(self, oidlist):
        """ Convert the oidlist to objectlist. """
        result = []
        for oid in oidlist:
            result.append(self.collection._get_object(oid))
        return result

    def __remove_multi_items(self, list):
        """ Removes multi occurences of items in a list (but keeps one). """
        mydict = {} # uses a dicts keys
        for elem in list:
            mydict[elem] = ""
        return [elem[0] for elem in mydict.items()]

    def _eajoin(self, elem1, elem2):
        """ Element-Attribute-Join. """
        elem1 = self._get_elem(elem1)
        elem2 = self._get_elem(elem2)
        return self.collection.eajoin(elem2, elem1)

    def _eejoin(self, elem1, elem2):
        """ Element-Element-Join. """
        elem1 = self._get_elem(elem1)
        if not elem1: # root join
            elem1 = [ self.collection.root() ]
        follow = []
        for elem in elem1:
            follow.extend(self._get_elem(elem2,
                        self.collection.get_structureindex(elem)))
        return self.collection.eejoin(follow, elem1, direct=True)

    def _get_elem(self, elem, structindex=None):
        """ Decide what to do with elem. """
        if not elem:                # elem is None
            return None
        elif elem[0] == "ELEM":     # elem is ("ELEM", "...")
            return self.collection.by_class(elem[1], structindex)
        elif elem[0] == "WILDCARD": # elem is ("WILDCARD", "_")
            return self.collection.all()
        elif elem[0] == "ATTR":     # elem is ["ATTR", (ID, VALUE)]
            return self.collection.by_attr(elem[1][0], elem[1][1])
        else:                       # elem is [function, ...]
            return self._process_queryplan(elem, structindex)

    def _kcjoin(self, occ, elem, structindex):
        """ Element-Occurence-Join. """
        elem = self._get_elem(elem, structindex)
        if (occ == "?" and len(elem) < 2):
            return elem
        elif (occ == "+" and len(elem) > 0):
            return elem
        elif (occ == "*"):
            return elem
        return []

    def _process_queryplan(self, qp, structindex=None):
        """ Recursive process of query plan ``qp``. """
        if qp[0] == "EEJOIN":
            result = self._eejoin(qp[1], qp[2])
        elif qp[0] == "EAJOIN":
            result = self._eajoin(qp[1], qp[2])
        elif qp[0] == "KCJOIN":
            result = self._kcjoin(qp[1], qp[2], structindex)
        elif qp[0] == "UNION":
            result = self._union(qp[1], qp[2])
        return result

    def _union(self, elem1, elem2):
        """ Union if two results. """
        elem1 = self._get_elem(elem1)
        elem1.extend(self._get_elem(elem2))
        return elem1
