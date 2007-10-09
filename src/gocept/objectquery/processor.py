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

    def __call__(self, expression):
        parse_tree = self.parser.parse(expression)
        return self._process_parse_tree(parse_tree)

    def _process_parse_tree(self, parse_tree):
        return gocept.objectquery.resultset.ResultSet()
