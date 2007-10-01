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
        normal          := PATH_SEPARATOR?, pathelem,
                           (PATH_SEPARATOR, pathelem)*
        pathelem        := (WILDCARD / ELEM), occurence?, predicate?
        predicate       := (PREDICATE_BEGIN, ID, '=', '"', ATTRVALUE, '"',
                            PREDICATE_END)
        occurence       := OCC_NONE_OR_ONE / OCC_ONE_OR_MORE / OCC_MULTI
        ID              := ELEM
        ELEM            := [a-zA-Z0-9]+
        ATTRVALUE       := text / quoted_text
        text            := [a-zA-Z0-9 ]+, quoted_text*
        quoted_text     := [a-zA-Z0-9 ]*, '\"', [a-zA-Z0-9 ]+, '\"',
                           [a-zA-Z0-9 ]*
        PATH_SEPARATOR  := '/'
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
            return None
        elif isinstance(result[0], basestring):
            if result[0] == "normal":
                return self._modify_result(result[3], expression, [])
            elif result[0] == "pathelem":
                rtemp = self._modify_result(result[3], expression, [])
                if output == []:
                    return rtemp
                else:
                    output.append(rtemp)
            elif result[0] == "occurence":
                rtemp = self._modify_result(result[3], expression, [])
                output = ['OCCJOIN', rtemp, output]
            elif result[0] == "predicate":
                rtemp = self._modify_result(result[3], expression, ["ATTR"])
                output = ['EAJOIN', rtemp, output]
            elif result[0] == "PATH_SEPARATOR":
                if output == []:
                    output = None
                output = ['EEJOIN', output]
            elif result[0] == "ELEM":
                return ("ELEM", expression[result[1]:result[2]])
            elif result[0] == "WILDCARD":
                return ("WILDCARD", expression[result[1]:result[2]])
            elif result[0] == "OCC_NONE_OR_ONE":
                return ("OCC", "?")
            elif result[0] == "OCC_ONE_OR_MORE":
                return ("OCC", "+")
            elif result[0] == "OCC_MULTI":
                return ("OCC", "*")
            elif result[0] == "ID":
                output.append(("ID", expression[result[1]:result[2]]))
            elif result[0] == "ATTRVALUE":
                output.append(("VALUE", expression[result[1]:result[2]]))
        else:
            for i in result:
                output = (self._modify_result(i, expression, output))
        return output


    def parse(self, expression):
        """ """

        if (expression is not None):
            succ, child, nextchar = self.parser.parse(expression, "rpe")
            if (not succ or (nextchar != len(expression))):
                raise SyntaxError("Wrong syntax in regular path expression")
        print self._modify_result(child, expression, [])
#        return child
