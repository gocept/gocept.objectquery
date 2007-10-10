# Copyright (c) 2007 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

class ObjectCollection:
    """ Holds objects and provides functionality on them. """
    def __init__(self, collection=None):
        """ initialize the collection """
        if collection is None:
            collection = []
        self.collection = collection

    def add(self, object):
        self.collection.append(object)

    def all(self):
        return self.collection

    def by_class(self, name, namespace):
        return [ elem for elem in self.collection
                        if elem.__class__.__name__ == name
                        and elem.__ns__[0] >= namespace[0]
                        and elem.__ns__[0] <= (namespace[0] + namespace[1])
               ]

    def by_attr(self, id, value):
        return [ elem for elem in self.collection
                        if hasattr(elem, id) and getattr(elem, id) == value ]

    def get_value(self, id):
        return [ getattr(elem, id) for elem in self.collection
                        if hasattr(elem, id) ]
