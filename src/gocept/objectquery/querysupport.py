# Copyright (c) 2007 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

import types

class ObjectParser(object):
    def __init__(self):
        self.attributes = []     # saves all found attributes to one object
        self.descendants = []    # saves all found descendands to one object

    def parse(self, object):
        self.__init__()
        if hasattr(object, "__dict__"):
            for x in object.__dict__.keys():
                self.attributes.append(x)
                if isinstance(object.__dict__[x], types.ListType):
                    self._traverse(object.__dict__[x])
                elif isinstance(object.__dict__[x], types.TupleType):
                    self._traverse(object.__dict__[x])
                elif isinstance(object.__dict__[x], types.DictType):
                    self._traverse(self._dict2list(object.__dict__[x]))
                elif str(type(object.__dict__[x])).startswith("<class"):
                    self.descendants.append(object.__dict__[x])

    def result(self, filter=None):
        if filter is not None:
            return getattr(self, filter)

    def _dict2list(self, dict):
        returnlist = []
        for elem in dict.values():
            if isinstance(elem, types.ListType):
                returnlist.extend(elem)
            elif isinstance(elem, types.TupleType):
                returnlist.extend(list(elem))
            elif isinstance(elem, types.DictType):
                returnlist.extend(self._dict2list(elem))
            else:
                returnlist.append(elem)
        return returnlist

    def _traverse(self, object):
        for elem in object:
            if str(type(elem)).startswith("<class"):
                self.descendants.append(elem)
