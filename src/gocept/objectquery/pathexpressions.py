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
        self.declaration = r'''
        rpe         := path, ('|', path)*
        path        := ((klammer / normal), occurence?, '|'?)+
        klammer     := '(', path+, ')'
        normal      := '/'?, pe, ('/', pe)*
        pe          := ('_' / IDENTIFIER), occurence?, predicate?
        predicate   := ('[', '@', IDENTIFIER, '=', '"', ATTRVALUE, '"', ']') 
        occurence   := '?' / '+' / '*'
        IDENTIFIER  := [a-zA-Z0-9]+
        ATTRVALUE   := [a-zA-Z0-9 ]+
        '''

    def check(self):
        parser = Parser(self.declaration)

    def parse(self, expression, level="rpe"):
        parser = Parser(self.declaration)
        success, children, nextcharacter = parser.parse(expression,
                                                        level)
        assert success and nextcharacter==len(expression), """Wasn't able to parse %s as a %s (%s chars parsed of %s), returned value was %s"""%(repr(expression), level, nextcharacter, len(expression), (success, children, nextcharacter))
