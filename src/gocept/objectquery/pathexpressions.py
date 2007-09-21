# Copyright (c) 2007 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

import gocept.objectquery.resultset
import StringIO
from simpleparse.common import numbers, strings, comments
from simpleparse.parser import Parser

class QueryProcessor(object):
    """ Processes a rpe query to the db and returns the results.

    QueryProcessor parses a regular path expression query by using
    SimpleParser. It returns a resultset object with the results from
    the database.
    """

    def __init__(self, collection):
        self.collection = collection

    def __call__(self, expression):
        return gocept.objectquery.resultset.ResultSet()

class QueryParser(object):
    """ """

    def __init__(self):
        declaration = r'''
        rpe         := path, ('|', path)*
        path        := ((bracket / normal), occurence?, '|'?)+
        bracket     := '(', path+, ')'
        normal      := '/'?, pathelem, ('/', pathelem)*
        pathelem    := ('_' / IDENTIFIER), occurence?, predicate?
        predicate   := ('[', '@', IDENTIFIER, '=', '"', ATTRVALUE, '"', ']') 
        occurence   := '?' / '+' / '*'
        IDENTIFIER  := [a-zA-Z0-9]+
        ATTRVALUE   := [a-zA-Z0-9 ]+
        '''
        self.parser = Parser(declaration)

    def check(self, expression=None, level="rpe"):
        """ Check expression for syntax errors. """

        if (expression is not None):
            succ, child, nextchar = self.parser.parse(expression, level)
            assert succ and nextchar==len(expression), """Wasn't able to "
                "parse %s as a %s (%s chars parsed of %s), returned value"
                 was %s"""%(repr(expression), level, nextchar,
                            len(expression), (succ, child, nextchar))

    def parse(self, expression):
        """ """

        succ, child, nextchar = self.parser.parse(expression, "rpe")
        return child
