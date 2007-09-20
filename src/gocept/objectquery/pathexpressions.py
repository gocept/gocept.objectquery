# Copyright (c) 2007 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

import gocept.objectquery.resultset
import reflex
import StringIO

class QueryProcessor(object):
    """ Processes a rpe query to the db and returns the results.

    QueryProcessor processes a regular path expression query by using
    reflex-0.1 from Talin <viridia at gmail com>. It returns a resultset
    object with the results from the database.
    """

    def __init__(self, collection):
        self._bracket_count = 0
        self.collection = collection
        self.lexer = self._init_lexer()

    def __call__(self, expression):
        if (expression == ''): 
            raise SyntaxError('Query must not be empty.')
        self.expression = StringIO.StringIO(expression)
        self.iterer = self.lexer( self.expression )
        for token in self.iterer:
            # do something with lexer
            self.temp = token.id    # DUMMY
        if (self._bracket_count != 0):
            raise SyntaxError('Open parenthesis count does not match close '
                              'parenthesis count')
        #print self._bracket_count
        return gocept.objectquery.resultset.ResultSet()

    def _inc_lexer_bracket(self, token_stream):
        """ Help method incrementing the count of paranthesises. """
        self._bracket_count = self._bracket_count + 1

    def _dec_lexer_bracket(self, token_stream):
        """ Help method decrementing the count of paranthesises. """
        if (self._bracket_count == 0):
            raise SyntaxError('Wrong closing paranthesis. No more open '
                              'paranthesises left.')
        self._bracket_count = self._bracket_count - 1

    def _init_lexer(self):
        """ Initialize the lexer with rpe rules.

        Here the lexer is being initialized with rules that match regular path
        expressions. Please read ***LINKDIPLOMATHESIS*** for more details.
        """

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
        self.scanner.rule("\(", self._inc_lexer_bracket, tostate="rpe", token=T_PREC_BEGIN)
        self.scanner.rule("/", tostate="subexp", token=T_PATHSEPERATOR)
        self.scanner.rule("[a-zA-Z0-9_][\w_]*", tostate="occ", token=T_STRING)

        self.scanner.state("subexp")
        self.scanner.rule("\)", self._dec_lexer_bracket, tostate="occ", token=T_PREC_END)
        self.scanner.rule("\(", self._inc_lexer_bracket, tostate="subexp", token=T_PREC_BEGIN)
        self.scanner.rule("/", tostate="subrpe", token=T_PATHSEPERATOR)
        self.scanner.rule("\|", tostate="subexp", token=T_UNION)
        self.scanner.rule("", tostate="subrpe")

        self.scanner.state("subrpe")
        self.scanner.rule("\(", self._inc_lexer_bracket, tostate="subrpe", token=T_PREC_BEGIN)
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
