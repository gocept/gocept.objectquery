# Copyright (c) 2007 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

import gocept.objectquery.resultset
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

    def __init__(self):
        declaration = r'''
        rpe             := ((bracket / normal), occurence?, UNION?)+
        bracket         := open_bracket, rpe+, close_bracket
        normal          := PATH_SEPERATOR?, pathelem, (PATH_SEPERATOR, pathelem)*
        pathelem        := (WILDCARD / IDENTIFIER), occurence?, predicate?
        predicate       := (PREDICATE_BEGIN, IDENTIFIER, '=', '"', ATTRVALUE, '"', PREDICATE_END)
        occurence       := OCC_NONE_OR_ONE / OCC_ONE_OR_MORE / OCC_MULTI
        IDENTIFIER      := [a-zA-Z0-9]+
        ATTRVALUE       := text / quoted_text
        text            := [a-zA-Z0-9 ]+, quoted_text*
        quoted_text     := [a-zA-Z0-9 ]*, '\"', [a-zA-Z0-9 ]+, '\"', [a-zA-Z0-9 ]*
        PATH_SEPERATOR  := '/'
        WILDCARD        := '_'
        UNION           := '|'
        open_bracket    := '('
        close_bracket   := ')'
        PREDICATE_BEGIN := '[@'
        PREDICATE_END   := ']'
        OCC_NONE_OR_ONE := '?'
        OCC_ONE_OR_MORE := '+'
        OCC_MULTI       := '*'
        '''
        self.parser = Parser(declaration)

    def _modify_result(self, result, expression, output):
        # stop condition
        if result is None:
            return output
        else:
            # Is result[0] a string? If yes, then do something with it
            if (isinstance(result[0], basestring)):
                # Is result[0] uppercase? If yes, then append it to the list
                # as {Identifier: Value}
                if (result[0] == result[0].upper()):
                    output.append({result[0]: expression[result[1]:result[2]]})
                # result[0] is not uppercase: go deeper
                else:
                    # is result[0] = "pathelem" oder "bracket":
                    # generate a subtupel
                    if ((result[0] == "pathelem") or (result[0] == "bracket")):
                        temp = output
                        output = self._modify_result(result[3],expression, [])
                        temp.append(output)
                        output = temp
                    # go deeper
                    else:
                        output = self._modify_result(result[3],expression,output)
            # result[0] is not a string, so it is a tupel
            # go deeper for each tupel
            else:
                for i in result:
                    output = self._modify_result(i,expression,output)
        return output

    def parse(self, expression):
        """ """

        if (expression is not None):
            succ, child, nextchar = self.parser.parse(expression, "rpe")
            if (not succ or (nextchar != len(expression))):
                raise SyntaxError("Wrong syntax in regular path expression")
        return self._modify_result(child, expression, [])
