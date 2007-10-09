# Copyright (c) 2007 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

class ObjectCollection:
    """ Holds Objects and gives functionality on them. """
    def __init__(self, collection=[]):
        """ initialize the collection """
        self.collection = collection

    def __call__(self, collection):
        """ is used for recursiveness - give it a "smaller" version """
        self.__init__(collection)

    def add(self, object):
        self.collection.append(object)

    def all(self):
        return self.collection
