# Copyright (c) 2007 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

from gocept.objectquery.resultset import ResultSet
import types

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
        result = self._process_qp(qp)
        return self._oids2objects(result)

    def _process_qp(self, qp, structindex=None):
        """ Recursive process of query plan ``qp``. """
        if not qp:
            return None
        func = getattr(self, "_process_" + qp[0])
        args = [qp[1], len(qp) >= 3 and qp[2] or None, structindex]
        return func(args)

    def _process_ELEM(self, args):
        """ Return all elements from ClassIndex with matching name.

        Returns all elements matching name in args[0] and structure index in
        args[2].
        """
        return self.collection.by_class(args[0], args[2])

    def _process_WILDCARD(self, args):
        """ Return all elements from ClassIndex. """
        return self.collection.all()

    def _process_ATTR(self, args):
        """ Return all elements from AttributeIndex matching name.

        Returns all elements matching name in args[0][0] and value in
        args[0][1] and comparative operator in args[0][2].
        """
        return self.collection.by_attr(args[0][0], args[0][1], args[0][2])

    def _process_EAJOIN(self, args):
        """ Element-Attribute-Join. """
        return self.collection.eajoin(self._process_qp(args[1]),
                                        self._process_qp(args[0]))

    def _process_EEJOIN(self, args):
        """ Element-Element-Join. """
        elemlist = self._process_qp(args[0])
        # make sure that elemlist is elemlist and not a pw-tupel
        attrname = None
        if type(elemlist) == types.TupleType:
            attrname = elemlist[1]
            elemlist = elemlist[0]
        elem1 = not elemlist and [ self.collection.root() ] or elemlist
        # only get the successors with are inside the parent StructureIndex
        successors = []
        for parent in elem1:
            successors.extend(self._process_qp(args[1],
                        self.collection.get_structureindex(parent)))
        return self.collection.eejoin(elem1, successors, direct=True,
                                                          way=attrname)

    def _process_PWJOIN(self, args):
        """ Path-Way-Join. """
        elemlist = self._process_qp(args[0])
        attrname = args[1][1]
        return (elemlist, attrname)

    def _process_KCJOIN(self, args):
        """ Element-Occurence-Join. """
        resultlist = self._process_qp(args[1], args[2])
        return self.collection.kcjoin(resultlist, args[0])

    def _process_UNION(self, args):
        """ Union if two results. """
        return self.collection.union(self._process_qp(args[0]),
                                            self._process_qp(args[1]))

    def _oids2objects(self, oidlist):
        """ Convert the oidlist to objectlist. """
        result = []
        for oid in oidlist:
            result.append(self.collection._get_object(oid))
        return result
