# Copyright (c) 2007-2008 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

import simpleparse.parser
from zope.interface import implements
from gocept.objectquery.interfaces import IQueryParser

class RPEQueryParser(object):
    """ Parses a rpe query and returns a readable result. """
    implements(IQueryParser)

    def __init__(self):
        declaration = r'''
        rpe             := expr, ((UNION / PATH_SEPARATOR), expr)?
        expr            := ((bracket / normal), occurence?)+
        bracket         := open_bracket, rpe+, close_bracket
        normal          := PATH_SEPARATOR?, pathelem,
                           (PATH_SEPARATOR, pathelem)*
        pathelem        := (WILDCARD / ELEM), pathway?, occurence?, predicate?
        predicate       := (PREDICATE_BEGIN, ID, COMPARER, '"', ATTRVALUE,
                           '"', PREDICATE_END)
        occurence       := OCC_NONE_OR_ONE / OCC_ONE_OR_MORE / OCC_MULTI
        pathway         := '.', WAY
        WAY             := ELEM
        ID              := ELEM
        ELEM            := [a-zA-Z0-9_]+
        ATTRVALUE       := text / quoted_text
        text            := [a-zA-Z0-9 ]*, quoted_text*
        quoted_text     := [a-zA-Z0-9 ]*, '\"', [a-zA-Z0-9 ]+, '\"',
                           [a-zA-Z0-9 ]*
        COMPARER        := COM_EQ / COM_LO_EQ / COM_GR_EQ / COM_GR / COM_LO /
                           COM_NOT_EQ
        PATH_SEPARATOR  := '/_*/' / '/'
        WILDCARD        := '_'
        UNION           := '|'
        open_bracket    := '('
        close_bracket   := ')'
        PREDICATE_BEGIN := '[@'
        PREDICATE_END   := ']'
        OCC_NONE_OR_ONE := '?'
        OCC_ONE_OR_MORE := '+'
        OCC_MULTI       := '*'
        COM_EQ          := '==' / '='
        COM_LO          := '<'
        COM_GR          := '>'
        COM_LO_EQ       := '<='
        COM_GR_EQ       := '>='
        COM_NOT_EQ      := '!='

        '''
        self.parser = simpleparse.parser.Parser(declaration)

    def _build_queryplan(self, result, expression, output):
        """ Modifies the SimpleParse result for better usability.

            SimpleParse returns the same result format as the one from the
            underlying mx.TextTools engine. This is for our approach not
            usable, so we must convert it into a better one.

            Imagine the following input query:

                p.parse('foo/bar')

            Here is what SimpleParse returns:

                [('expr', 0, 7,
                  [('normal', 0, 7,
                    [('pathelem', 0, 3,
                      [('ELEM', 0, 3, None)]),
                     ('PATH_SEPARATOR', 3, 4, None),
                     ('pathelem', 4, 7,
                       [('ELEM', 4, 7, None)]
                    )]
                  )]
                )]

            And here, what we want and what _build_queryplan returns:

                ['EEJOIN',
                  ('ELEM', 'foo'),
                  ('ELEM', 'bar')
                ]
        """

        if isinstance(result[0], basestring):
            if result[0] == "rpe":
                return self._build_queryplan(result[3], expression, [])
            elif result[0] == "expr":
                return self._build_queryplan(result[3], expression, output)
            elif result[0] == "normal":
                return self._build_queryplan(result[3], expression, output)
            elif result[0] == "bracket":
                rtemp = self._build_queryplan(result[3], expression, [])
                if output != []:
                    output.append(['PREC', rtemp])
                else:
                    output = ['PREC', rtemp];
                return output
            elif result[0] == "pathelem":
                rtemp = self._build_queryplan(result[3], expression, [])
                if output == []:
                    output = rtemp
                else:
                    output.append(rtemp)
            elif result[0] == "occurence":
                rtemp = self._build_queryplan(result[3], expression, [])
                output = ['KCJOIN', rtemp, output]
            elif result[0] == "predicate":
                rtemp = self._build_queryplan(result[3], expression, [])
                rtemp = (rtemp[0], rtemp[2], rtemp[1])
                rtemp = ["ATTR", rtemp]
                output = ['EAJOIN', rtemp, output]
            elif result[0] == "pathway":
                rtemp = self._build_queryplan(result[3], expression, [])
                output = ['PWJOIN', output, rtemp]
            elif result[0] == "PATH_SEPARATOR":
                seperator = expression[result[1]:result[2]]
                if output == []:
                    output = None
                if seperator == '/':
                    output = ['EEJOIN', output]
                else:
                    output = ['EEJOIN', output, seperator]
            elif result[0] == "UNION":
                output = ['UNION', output]
            elif result[0] == "ELEM":
                return ("ELEM", expression[result[1]:result[2]])
            elif result[0] == "WAY":
                return ("WAY", expression[result[1]:result[2]])
            elif result[0] == "WILDCARD":
                return ("WILDCARD", expression[result[1]:result[2]])
            elif result[0] == "OCC_NONE_OR_ONE":
                return "?"
            elif result[0] == "OCC_ONE_OR_MORE":
                return "+"
            elif result[0] == "OCC_MULTI":
                return "*"
            elif result[0] == "ID":
                output.append(expression[result[1]:result[2]])
            elif result[0] == "ATTRVALUE":
                output.append(expression[result[1]:result[2]])
            elif result[0] == "COMPARER":
                output.append(expression[result[1]:result[2]])
        else:
            for i in result:
                output = (self._build_queryplan(i, expression, output))
        return output

    def parse(self, expression):
        """ Parse the expression and return a query_plan. """

        if (expression is not None):
            succ, child, nextchar = self.parser.parse(expression, "rpe")
            if (not succ or nextchar != len(expression)):
                raise SyntaxError("Wrong syntax in regular path expression.")
        return self._build_queryplan(child, expression, [])
