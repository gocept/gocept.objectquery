# Copyright (c) 2007 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

class ResultSet(object):
    def __init__(self):
        self.result = []
    def add(self, object):
        self.result.append(object)
    def remove(self, object):
        self.result = [ elem for elem in self.result
                            if elem != object ]
    def list(self):
        return self.result
