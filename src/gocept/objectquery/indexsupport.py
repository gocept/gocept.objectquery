# Copyright (c) 2007 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

class PathIndex(object):
    def __init__(self, path=None):
        if path is None:
            path = []
        self.path = path
        self.childs = []

    def bear(self, handle):
        new_path = []
        new_path.extend(self.path)
        new_path.append(handle)
        newchild = PathIndex(new_path)
        self.childs.append(newchild)
        return newchild

    def _rearrange_index(self, replace):
        self.path = replace[1] + self.path[replace[0]:]
        for elem in self.childs:
            elem._rearrange_index(replace)

    def move(self, child, target):
        replace = (len(self.path), target.path)
        self.childs.remove(child)
        target.childs.append(child)
        child._rearrange_index(replace)

    def is_direct_parent(self, child):
        if child in self:
            if len(self.path)+1 == len(child.path):
                return True
        return False

    def __contains__(self, child):
        # PathIndex length of child must be longer than self ones
        if len(self.path) > len(child.path):
            return False
        for index in xrange(len(self.path)):
            if self.path[index] is not child.path[index]:
                return False
        return True

    def __repr__(self):
        return "<" + self.__module__ + ".PathIndex object with path '"\
               + ', '.join( [str(x) for x in self.path] ) + "'>"

class ElementIndex(object):
    def __init__(self):
        self.__index = {}
        self.__root = None

    def add(self, object, parent=None):
        if parent is None:
            if self.__index != {}:
                raise KeyError('There is already a root object defined: ' +\
                              str(self.__root))
            self.__index[object] = []
            self.__root = object
        else:
            self.__index[parent].append(object)
            if self.__index.get(object, None) is None:
                self.__index[object] = []

    def delete(self, object, parent=None):
        if (parent is None) and (object == self.__root):
            self.__init__()
        else:
            while object in self.__index[parent]:
                self.__index[parent].remove(object)
            if object not in self.rlist():
                del self.__index[object]

    def move(self, object, parent, target):
        self.__index[target].append(object)
        self.delete(object, parent)

    def list(self, object=None):
        if object is None:
            object = self.__root
        return self.__index[object]

    def rlist(self, object=None):
        if object is None:
            object = self.__root
        if object is None:
            return []
        returnlist = [object]
        for elem in self.__index[object]:
            returnlist.extend(self.rlist(elem))
        return returnlist

    def root(self):
        return self.__root
