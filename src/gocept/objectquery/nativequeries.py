# Copyright (c) 2008 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

class NativeQueries(object):
    """ Native Queries """

    def __init__(self, database=None):
        self.database = []
        if database is not None:
            self.database = database

    def __call__(self, query):
        self.response = []
        for elem in self.database:
            try:
                if query(elem) == True:
                    self.response.append(elem)
            except (TypeError): pass
        return self.response

    def register_database(self, database):
        self.database = database
