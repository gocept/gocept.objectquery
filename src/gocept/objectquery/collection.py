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

    def by_class(self, name):
        return [elem for elem in self.collection
                        if elem.__class__.__name__ == name]

    def by_attr(self, id, value):
        return [elem for elem in self.collection
                        if hasattr(elem,id) and getattr(elem,id) == value]

    def get_value(self, id):
        return [getattr(elem,id) for elem in self.collection
                        if hasattr(elem,id)]
