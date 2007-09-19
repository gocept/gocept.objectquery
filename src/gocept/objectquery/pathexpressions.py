# Copyright (c) 2007 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

import gocept.objectquery.resultset
import reflex
import StringIO

class QueryProcessor(object):

    def __init__(self, collection):
        self._bracket_count = 0
        self.collection = collection
        self.lexer = self._init_lexer()

    def __call__(self, expression):
        if (expression == ''): 
            raise SyntaxError('Query must not be empty.')
        self.expression = StringIO.StringIO(expression)
        self.iterer = self.lexer( self.expression )
        # do something with lexer (dummy begin)
        for token in self.iterer:
            self.temp = token.id
        # (dummy end)
        if (self._bracket_count != 0):
            raise SyntaxError('Open parenthesis count does not match close '
                              'parenthesis count')
        return gocept.objectquery.resultset.ResultSet()

    def _inc_lexer_bracket(self, token_stream):
        self._bracket_count = self._bracket_count + 1

    def _dec_lexer_bracket(self, token_stream):
        self._bracket_count = self._bracket_count - 1

    def _init_lexer(self):
        """ init the lexer with RPE rules """

        T_PATHSEPERATOR = 1
        T_UNION = 2
        T_OCC_ONE = 5
        T_OCC_ONE_OR_MORE = 6
        T_OCC_MULTI = 7
        T_STRING = 10
        T_ATTR_KEY = 11
        T_ATTR_VALUE = 12
        T_PREC_BEGIN = 15
        T_PREC_END = 16

        self.scanner = reflex.scanner("rpe")
        self.scanner.rule("\(", self._inc_lexer_bracket, tostate="rpe")
        self.scanner.rule("/", tostate="subexp", token=T_PATHSEPERATOR)
        self.scanner.rule("[a-zA-Z0-9_][\w_]*", tostate="occ", token=T_STRING)

        self.scanner.state("subexp")
        self.scanner.rule("\)", self._dec_lexer_bracket, tostate="occ")
        self.scanner.rule("\(", self._inc_lexer_bracket, tostate="subexp")
        self.scanner.rule("/", tostate="subrpe", token=T_PATHSEPERATOR)
        self.scanner.rule("\|", tostate="subexp", token=T_UNION)
        self.scanner.rule("", tostate="subrpe")

        self.scanner.state("subrpe")
        self.scanner.rule("\(", self._inc_lexer_bracket, tostate="subrpe")
        self.scanner.rule ("[a-zA-Z0-9_][\w_]*", tostate="occ", token=T_STRING)

        self.scanner.state( "occ" )
        self.scanner.rule ("\?", tostate="predicate", token=T_OCC_ONE)
        self.scanner.rule ("\+", tostate="predicate", token=T_OCC_ONE_OR_MORE)
        self.scanner.rule ("\*", tostate="predicate", token=T_OCC_MULTI)
        self.scanner.rule ("", tostate="predicate")

        self.scanner.state("predicate")
        self.scanner.rule ("\[@", tostate="predicate_expl")
        self.scanner.rule("", tostate="subexp")

        self.scanner.state("predicate_expl")
        self.scanner.rule ("[a-zA-Z0-9_][\w_]*", token=T_ATTR_KEY)
        self.scanner.rule ("=\"")
        self.scanner.rule ("[a-zA-Z0-9 _][\w_]*", token=T_ATTR_VALUE)
        self.scanner.rule ("\"\]", tostate="subexp")

        return self.scanner
