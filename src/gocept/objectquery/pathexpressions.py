# Copyright (c) 2007 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

import gocept.objectquery.resultset
import StringIO
from simpleparse.common import numbers, strings, comments
from simpleparse.parser import Parser
from simpleparse.dispatchprocessor import *

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

    def __init__(self):
        declaration = r'''
        rpe             := ((bracket / normal), occurence?, UNION?)+
        bracket         := OPEN_BRACKET, rpe+, CLOSE_BRACKET
        normal          := PATH_SEPERATOR?, pathelem, (PATH_SEPERATOR, pathelem)*
        pathelem        := (WILDCARD / IDENTIFIER), occurence?, predicate?
        predicate       := (PREDICATE_BEGIN, IDENTIFIER, '=', '"', ATTRVALUE, '"', PREDICATE_END)
        occurence       := OCC_NONE_OR_ONE / OCC_ONE_OR_MORE / OCC_MULTI
        IDENTIFIER      := [a-zA-Z0-9]+
        ATTRVALUE       := [a-zA-Z0-9 ]+
        PATH_SEPERATOR  := '/'
        WILDCARD        := '_'
        UNION           := '|'
        OPEN_BRACKET    := '('
        CLOSE_BRACKET   := ')'
        PREDICATE_BEGIN := '[@'
        PREDICATE_END   := ']'
        OCC_NONE_OR_ONE := '?'
        OCC_ONE_OR_MORE := '+'
        OCC_MULTI       := '*'
        '''
        self.parser = Parser(declaration)

    def _modify_result(self, result, expression, output=[]):
        if result is None:
            return output
        else:
            if (isinstance(result[0], basestring)):
                if (result[0] == result[0].upper()):
                    output.append({result[0]: expression[result[1]:result[2]]})
                else:
                    output = self._modify_result(result[3],expression,output)
            else:
                for i in result:
                    output = self._modify_result(i,expression,output)
        return output

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

        if (expression is not None):
            succ, child, nextchar = self.parser.parse(expression, "rpe")
            assert succ and nextchar==len(expression), """Wasn't able to "
                "parse %s as a %s (%s chars parsed of %s), returned value"
                 was %s"""%(repr(expression), level, nextchar,
                            len(expression), (succ, child, nextchar))
        return self._modify_result(child, expression, [])
#        return child
