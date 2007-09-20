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
        self.collection = collection

    def __call__(self, expression):
        return gocept.objectquery.resultset.ResultSet()


T_PATHSEPERATOR = 'pathsep'
T_UNION = 'operator'
T_OCC_ONE = 'once'
T_OCC_ONE_OR_MORE = 'once-or-more'
T_OCC_MULTI = 'zero-or-more'
T_STRING = 'string'
T_ATTR_KEY = 'attribute-key'
T_ATTR_VALUE = 'attribute-value'
T_PREC_BEGIN = 'bracket-left'
T_PREC_END = 'bracket-right'


class Lexer(object):

    def __init__(self):
        self.scanner = reflex.scanner("rpe")
        self.scanner.rule("\(", tostate="rpe", token=T_PREC_BEGIN)
        self.scanner.rule("/", tostate="subexp", token=T_PATHSEPERATOR)
        self.scanner.rule("[a-zA-Z0-9_][\w_]*", tostate="occ", token=T_STRING)

        self.scanner.state("subexp")
        self.scanner.rule("\)", tostate="occ", token=T_PREC_END)
        self.scanner.rule("\(", tostate="subexp", token=T_PREC_BEGIN)
        self.scanner.rule("/", tostate="subrpe", token=T_PATHSEPERATOR)
        self.scanner.rule("\|", tostate="subexp", token=T_UNION)
        self.scanner.rule("", tostate="subrpe")

        self.scanner.state("subrpe")
        self.scanner.rule("\(", tostate="subrpe", token=T_PREC_BEGIN)
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

    def lex(self, expression):
        expression = StringIO.StringIO(expression)
        result = []
        for token in self.scanner(expression):
            result.append((token.id, token.value))
            return result
