# Copyright (c) 2007 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

import gocept.objectquery.resultset
import reflex
import StringIO

class QueryProcessor(object):
    """ """

    def __init__(self, collection):
        self.collection = collection
        self.lexer = self._init_lexer()

    def __call__(self, expression):
        """ """
        self.expression = StringIO.StringIO(expression)
        self.iterer = self.lexer( self.expression )
        for token in self.iterer:
            self.temp = token.id
        return gocept.objectquery.resultset.ResultSet()

    def _init_lexer(self):
        """ init the lexer with RPE rules """
        T_PATHSEPERATOR = 1
        T_UNION = 2
        T_OCC_ONE = 5
        T_OCC_ONE_OR_MORE = 6
        T_OCC_MULTI = 7
        T_STRING = 10
        T_PRECEDENCE_BEGIN = 15
        T_PRECEDENCE_END = 16

        self.scanner = reflex.scanner("rpe")
        self.scanner.rule("/", tostate="subexp", token=T_PATHSEPERATOR)

        self.scanner.state("subexp")
        self.scanner.rule("/", tostate="subrpe", token=T_PATHSEPERATOR)
        self.scanner.rule("\|", tostate="subexp", token=T_UNION)
        self.scanner.rule("", tostate="subrpe")

        self.scanner.state("subrpe")
        self.scanner.rule ("[a-zA-Z1-9_][\w_]*", tostate="occ", token=T_STRING)

        self.scanner.state( "occ" )
        self.scanner.rule ("\?", tostate="predicate", token=T_OCC_ONE)
        self.scanner.rule ("\+", tostate="predicate", token=T_OCC_ONE_OR_MORE)
        self.scanner.rule ("\*", tostate="predicate", token=T_OCC_MULTI)
        self.scanner.rule ("", tostate="predicate")

        self.scanner.state("predicate")
        self.scanner.rule("", tostate="subexp")

        return self.scanner
