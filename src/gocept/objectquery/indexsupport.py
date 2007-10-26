# Copyright (c) 2007 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

class ObjectToId(object):
    def __init__(self):
        self.__idlist = {}

    def obj2id(self, obj):
        self.__idlist[id(obj)] = obj
        return id(obj)

    def id2obj(self, id):
        return self.__idlist[id]


class PathIndex(object):
    """ PathIndex is used to quickly determine relationshops between objects.
    
        The first PathIndex is created the regular way. (pi = PathIndex())
        All new child PathIndexes must be created using the method ``bear()``,
        which returns a new PathIndex object. (child_pi = pi.bear("foo"))
    """
    def __init__(self):
        self.path = []
        self.childs = [] # we need a list of child PathIndexes in self.move()

    def __contains__(self, child):
        """ Check if child is in self. """
        # PathIndex length of child must be longer than self ones
        if len(self.path) > len(child.path):
            return False
        # All items of self.path must match the equivalent ones in child.path
        for index in xrange(len(self.path)):
            if self.path[index] is not child.path[index]:
                return False
        return True

    def __repr__(self):
        """ Returns a string like <PathIndex object with path 'foo'>. """
        return "<" + self.__module__ + ".PathIndex object with path '"\
               + ', '.join( [str(x) for x in self.path] ) + "'>"


    def _rearrange_path(self, replace):
        """ Recursive rearrange the path. Used within move function.

            Replace is a tuple (number, list) where number is the number of
            listitems, which have to be replaced and list is a list with items
            for replacement.
        """

        self.path = replace[1] + self.path[replace[0]:] # replace the path
        for elem in self.childs:
            elem._rearrange_path(replace) # replace for childs


    def bear(self, handle):
        """ Create a new PathElement as a child of self. """
        new_path = self.path[:] # copy parent path to child path
        new_path.append(handle)
        newchild = PathIndex()
        newchild.path = new_path
        self.childs.append(newchild)
        return newchild

    def delete(self, child):
        """ Delete child PathIndex from self. """
        if child in self.childs:
            self.childs.remove(child)   # subchilds are removed by Garbade

    def move(self, child, target):
        """ Move child from self to target. """

        # replace is describes in docstring of _rearrange_path
        replace = (len(self.path), target.path) # create replace tuple
        self.childs.remove(child)
        target.childs.append(child)
        child._rearrange_path(replace)


    def is_direct_parent(self, child):
        """ Check if self is a direct parent of child.

            First check if child is in self. If True, check, if path length of
            self is by one smaller than path length of child.
        """

        if child in self:
            if (len(self.path) + 1) == len(child.path):
                return True
        return False


class ElementIndex(object):
    """ ElementIndex is a dict to handle parent-child relationships. """
    def __init__(self):
        self.__index = {}
        self.__root = None

    def add(self, object, parent=None):
        """ Add an element under parent. """
        if parent is None: # no parent -> add as root
            # raise exception if we have already a root object
            if self.__root is not None:
                raise KeyError('There is already a root object defined: ' +\
                              str(self.__root))
            self.__index[object] = []
            self.__root = object
        else:
            self.__index[parent].append(object) # add object to parent list
            if self.__index.get(object, None) is None:
                self.__index[object] = [] # add objects parent list

    def delete(self, object, parent=None):
        """ Delete object under parent. """
        if (parent is None) and (object == self.__root): # delete root
            self.__init__()
        else:
            # delete every object under parent
            while object in self.__index[parent]:
                self.__index[parent].remove(object)
            if object not in self.rlist(): # object does not exist anymore
                del self.__index[object]

    def move(self, object, parent, target):
        """ Move object from parent to target. """
        # Get a list of objects to copy
        copylist = [elem for elem in self.__index[parent] if elem == object]
        for elem in copylist:
            self.__index[target].append(elem) # copy every object under target
        self.delete(object, parent) # delete them under parent


    def list(self, object=None):
        """ Return a list of direct childs under object. """
        if object is None:
            object = self.__root
        return self.__index[object]

    def rlist(self, object=None):
        """ Return a list of all childs under object (preorder).

            This includes the object as first element.
        """
        if object is None:
            object = self.__root
        if object is None:
            return []
        returnlist = [object]
        for elem in self.__index[object]:
            returnlist.extend(self.rlist(elem)) # recursion
        return returnlist

    def root(self):
        """ Return the root object. """
        return self.__root
