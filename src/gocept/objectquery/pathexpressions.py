# Copyright (c) 2007 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

import simpleparse.parser

class RPEQueryParser(object):
    """ Parses a rpe query and returns a readable result. """
    def __init__(self):
        declaration = r'''
        rpe             := expr, ((UNION / PATH_SEPARATOR), expr)?
        expr            := ((bracket / normal), occurence?)+
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
        self.parser = simpleparse.parser.Parser(declaration)

    def _modify_result(self, result, expression, output):
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

            And here, what we want and what _modify_result returns:

                ['EEJOIN',
                  ('ELEM', 'foo'),
                  ('ELEM', 'bar')
                ]
        """

        if result is None:
            return None
        elif isinstance(result[0], basestring):
            if result[0] == "rpe":
                return self._modify_result(result[3], expression, [])
            elif result[0] == "expr":
                return self._modify_result(result[3], expression, output)
            elif result[0] == "normal":
                return self._modify_result(result[3], expression, output)
            elif result[0] == "bracket":
                rtemp = self._modify_result(result[3], expression, [])
                if output != []:
                    output.append(rtemp)
                else:
                    output = rtemp;
                return output
            elif result[0] == "pathelem":
                rtemp = self._modify_result(result[3], expression, [])
                if output == []:
                    output = rtemp
                else:
                    if rtemp == []:
                        output.append(None)
                    else:
                        output.append(rtemp)
            elif result[0] == "occurence":
                rtemp = self._modify_result(result[3], expression, [])
                output = ['KCJOIN', rtemp, output]
            elif result[0] == "predicate":
                rtemp = self._modify_result(result[3], expression, ["ATTR"])
                output = ['EAJOIN', rtemp, output]
            elif result[0] == "PATH_SEPARATOR":
                if output == []:
                    output = None
                output = ['EEJOIN', output]
            elif result[0] == "UNION":
                if output == []:
                    output = None
                output = ['UNION', output]
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
            if (not succ or nextchar != len(expression)):
                raise SyntaxError("Wrong syntax in regular path expression.")
        return self._modify_result(child, expression, [])
