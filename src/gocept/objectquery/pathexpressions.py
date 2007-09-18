# Copyright (c) 2007 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

import gocept.objectquery.resultset


class QueryProcessor(object):
    """ """

    def __init__(self, collection):
        self.collection = collection

    def __call__(self, expression):
        """ """
        return gocept.objectquery.resultset.ResultSet()


