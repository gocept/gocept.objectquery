# Copyright (c) 2007 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

import types

class ObjectToId(object):
    def __init__(self):
        self.__idlist = {}

    def obj2id(self, obj):
        if obj is None:
            return None
        self.__idlist[id(obj)] = obj
        return id(obj)

    def id2obj(self, id):
        if id is None:
            return None
        return self.__idlist.get(id, 0)


class ObjectParser(object):
    """ Returns a dict of attributes which refer to another object. """
    def __init__(self):
        pass

    def __call__(self, object):
        return self._traverse(object)

    def __dict2list(self, dict):
        returnlist = []
        for elem in dict.values():
            if isinstance(elem, types.ListType):
                returnlist.extend(elem)
            elif isinstance(elem, types.TupleType):
                returnlist.extend(list(elem))
            elif isinstance(elem, types.DictType):
                returnlist.extend(self.__dict2list(elem))
            else:
                returnlist.append(elem)
        return returnlist

    def _traverse(self, object):
        attrlist = {}
        if hasattr(object, "__dict__"):
            for x in object.__dict__.keys():
                if isinstance(object.__dict__[x], types.ListType):
                    attrlist[x] = object.__dict__[x]
                elif isinstance(object.__dict__[x], types.TupleType):
                    attrlist[x] = list(object.__dict__[x])
                elif isinstance(object.__dict__[x], types.DictType):
                    attrlist[x] = self.__dict2list(object.__dict__[x])
                elif str(type(object.__dict__[x])).startswith("<class"):
                    attrlist[x] = [object.__dict__[x]]
        return attrlist


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
        self._index = {}
        self.__root = None

    def _add_root(self, object):
        """ Add an element as root. """
        # raise exception if we have already a root object
        if self.root() is not None:
            raise KeyError('There is already a root object defined: ' +\
                           str(self.__root))
        self._index[object] = []
        self.__root = object

    def add(self, object, parent=None):
        """ Add an element under parent. """
        if parent is None: # no parent -> add as root
            self._add_root(object)
        else:
            self._index[parent].append(object) # add object to parent list
            if self._index.get(object, None) is None:
                self._index[object] = [] # add objects parent list

    def delete(self, object, parent=None):
        """ Delete object under parent. """
        if (parent is None) and (object == self.root()): # delete root
            self.__init__()
        else:
            # delete every object under parent
            while object in self._index[parent]:
                self._index[parent].remove(object)
            if object not in self.rlist(): # object does not exist anymore
                del self._index[object]

    def move(self, object, parent, target):
        """ Move object from parent to target. """
        # Get a list of objects to copy
        copylist = [elem for elem in self._index[parent] if elem == object]
        for elem in copylist:
            self._index[target].append(elem) # copy every object under target
        self.delete(object, parent) # delete them under parent


    def list(self, object=None):
        """ Return a list of direct childs under object. """
        if object is None:
            object = self.root()
        return self._index[object]

    def rlist(self, object=None):
        """ Return a list of all childs under object (preorder).

            This includes the object as first element.
        """
        if object is None:
            object = self.root()
        if object is None:
            return []
        returnlist = [object]
        for elem in self._index[object]:
            returnlist.extend(self.rlist(elem)) # recursion
        return returnlist

    def root(self):
        """ Return the root object. """
        return self.__root


class AttributeIndex(object):
    """ AttributeIndex is a dict saving attributes between objects. """
    def __init__(self):
        self._index = {}

    def add(self, object, parent, attribute):
        if self._index.get(parent, None) is None:
            self._index[parent] = {}
        if self._index[parent].get(object, None) is None:
            self._index[parent][object] = []
        self._index[parent][object].append(attribute)

    def delete(self, object, parent, attribute=None):
        if attribute is None:
            return      # TODO: do something more here
        else:
            self._index[parent][object].remove(attribute)
        if self._index[parent][object] == []:
            del self._index[parent][object]
            if self._index[parent] == {}:
                del self._index[parent]

    def move(self, object, parent, attribute, newparent, newattribute):
        self.delete(object, parent, attribute)
        self.add(object, newparent, newattribute)

    def is_reachable(self, object, parent, attribute):
        if self._index.get(parent, None) is None:
            return False
        if self._index[parent].get(object, None) is None:
            return False
        if attribute not in self._index[parent][object]:
            return False
        return True

    def list_attributes(self, parent, object):
        if self._index.get(parent, None) is None:
            return []
        if self._index[parent].get(object, None) is None:
            return []
        return self._index[parent][object]

class CycleSupport(ElementIndex):
    """ Prevent the ObjectCollection from running into cycles.

        This is done by saving for each object the parent object. Before adding
        an object, CycleSupport looks through all parent objects until root,
        if the object, which will be added, already exists. If so, return
        False.
    """

    def add(self, object, parent=None):
        """ Add parent for object. """
        if parent is None: # no parent -> add as root
            self._add_root(object)
        else:
            if self._index.get(object, None) is None:
                self._index[object] = [parent]
            else:
                self._index[object].append(parent)

    def check_for_cycles(self, objectlist, parent):
        """ Checks, if adding object under parent results in a cycle. """
        for elem in self.rlist(parent):
            if elem in objectlist:
                return False
        return True

    def delete(self, object, parent=None):
        """ Delete parent from object. """
        if (parent is None) and (object == self.root()): # delete root
            self.__init__()
        else:
            # delete every parent from object
            while parent in self._index[object]:
                self._index[object].remove(parent)
            if self._index[object] == []:  # object does not exist anymore
                del self._index[object]

    def move(self, object, parent, target):
        """ Move object from parent to target. """
        for elem in [elem for elem in self._index[object] if elem == parent]:
            self._index[object].remove(parent)
        self._index[object].append(target)
