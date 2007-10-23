# Copyright (c) 2007 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

import types

MAX_CHILD = 10
MAX_HEIGHT = 5
ROOT_NAMESPACE = (1, MAX_CHILD**MAX_HEIGHT+1)

class RootObject(object):
    pass

class PathIndex(object):
    def __init__(self, path=None):
        if path is None:
            path = []
        self.path = path

    def bear(self, handle):
        new_path = []
        new_path.extend(self.path)
        new_path.append(handle)
        return PathIndex(new_path)

    def is_direct_parent(self, child):
        if child in self:
            if len(self.path)+1 == len(child.path):
                return True
        return False

    def __contains__(self, child):
        # PathIndex length child must be longer than self ones
        if len(self.path) >= len(child.path):
            return False
        for index in xrange(len(self.path)):
            if self.path[index] is not child.path[index]:
                return False
        return True

    def __repr__(self):
        return "<" + self.__module__ + ".PathIndex object with path '"\
               + ', '.join( [str(x) for x in self.path] ) + "'>"

class ElementIndex(object):
    pass

class ObjectCollection(object):
    """Holds objects and provides functionality on them."""
    def __init__(self, init_namespace=None):
        # Set the namespace size
        if init_namespace is None:
            init_namespace = (MAX_CHILD, MAX_HEIGHT)
        self.MAX_CHILD, self.MAX_HEIGHT = init_namespace
        self.root_namespace = (1, self.MAX_CHILD**self.MAX_HEIGHT+1)
        root = RootObject()
        # collection holds all elements once
        self.collection = [root]
        # _namespace is a tupel for each element consisting of an
        #  - order value which indicates the position in preorder
        #  - size value which is a range of order values of the subsequent
        #    elements
        self._namespace = {root: [[self.root_namespace]]}
        # _eeindex is a dict which holds all direct childs of elements in a
        # list. Used to compare direct relationships between elements.
        self._eeindex = {root: []}
        # _eenumber is a counter which holds the number of equal elements
        self._eenumber = {root: 1}

    def _compare_namespace(self, object_namespace, parent_namespace, level=0):
        """Return true if object_namespace is inside parent_namespace"""
        # Test if we have to go deeper in extended namespace
        if object_namespace[level] == parent_namespace[level] \
           and len(parent_namespace)-1 > level:
            return self._compare_namespace(object_namespace, parent_namespace,
                                           level+1)
        # Now test if the actual namespace level maches the object/parent
        elif object_namespace[level][0] >= parent_namespace[level][0] \
           and object_namespace[level][0] <= (parent_namespace[level][0] + \
                                       parent_namespace[level][1]):
            return True
        return False

    def _get_sons(self, object, parent_namespace):
        """Returns a list of elements which are direct sons of object

            object is the element for which sons should be returned.
            parent_namespace is the namespace in which sons should be searched.
            This is needed if objects exists more than once within your
            Collection.

        """

        sons = []
        for elem in self._eeindex[object]:
            if elem not in sons:    # prevent bi-insertion
                for object_namespace in self._namespace[elem]:
                    if self._compare_namespace(object_namespace,
                                               parent_namespace):
                        sons.append(elem)
        return sons

    def _get_new_namespace(self, object):
        """Return a list of new free namespace tupels under object

            The returned list consists of 1+ (order, size) tupels for each
            object found in your Collection.

        """
        new_namespaces = []
        # First we need to find out, if we need a namespace for a new amount
        # of sons (e.g. add an object as successor to another object, which
        # occurs more than once in your Collection) or if we just "subadd"
        # objects within the add of another add (recursive) - so we don't want
        # to add the subadds to perhaps existing objects.
        object_namespaces = self._namespace[object]
        old_sons = 0
        max_sons = 0
        namespace_update = False
        for object_namespace in object_namespaces:
            sons = len(self._get_sons(object, object_namespace))
            if sons < old_sons:
                namespace_update = True
            if sons > max_sons:
                max_sons = sons
            old_sons = sons

        # Now we are ready to get the new namespaces.
        for object_namespace in object_namespaces:
            new_namespace = []
            level = len(object_namespace)-1 # do something with the deepest ns
            # copy the higher namespace to the new one
            for bla in object_namespace[:-1]:
                new_namespace.append(bla)
            sons = len(self._get_sons(object, object_namespace))
            if sons >= self.MAX_CHILD:
                raise ValueError("Maximum number of childs exeeded (%i)"
                                 % self.MAX_CHILD)
            elif not namespace_update or sons < max_sons:
                # calculate new (order, size) tupel
                block_value = object_namespace[level][1] / self.MAX_CHILD
                order_value = object_namespace[level][0] + 1 + \
                                (block_value * sons)
                size_value = block_value - 1
                new_namespace.append((order_value, size_value))
                # dynamic namespace expansion
                if size_value < self.MAX_CHILD**2-1:
                    new_namespace.append(self.root_namespace)
                new_namespaces.append( new_namespace )
        return new_namespaces

    def index(self, object):
        """Call this function from outside to recursivly index object"""
        self.add(object, self.collection[0], index_call=True)

    def add(self, object, parent, index_call=False):
        """Add object (and subobjects) to Collection under parent"""
        # We only add instantiated classes
        if str(type(object)).startswith("<class"):
            # Get a new namespace and add is to _namespace[object]
            if self._namespace.get(object, None) is None:
                self._namespace[object] = []
            new_namespaces = self._get_new_namespace(parent)
            if index_call == True:      # bugfix
                new_namespaces = [ new_namespaces[-1] ]
            self._namespace[object].extend(new_namespaces)
            # Add object to parent _eeindex and add object _eeindex
            self._eeindex[parent].append(object)
            if self._eeindex.get(object, None) is None:
                self._eeindex[object] = []
            # Increment _eenumber
            if self._eenumber.get(object, None) is None:
                self._eenumber[object] = 0
            self._eenumber[object] = self._eenumber[object] + \
                                     len(new_namespaces)
            # Add object to collection
            if not object in self.collection:
                self.collection.append(object)
        # Look through objects __dict__ for classes and tupels or the like.
        if hasattr(object, "__dict__"):
            for x in object.__dict__.keys():
                # Is x a list or a tuple, then traverse it and add the
                # content.
                if isinstance(object.__dict__[x],
                              types.ListType) or isinstance(object.__dict__[x],
                                                            types.TupleType):
                    for y in object.__dict__[x]:
                        self.add(y, object, index_call)
                # Is x a dictionary, then traverse it and add the content.
                elif isinstance(object.__dict__[x], types.DictType):
                    for y in object.__dict__[x].keys():
                        self.add(object.__dict__[x][y], object, index_call)
                # Is x another class, then add it.
                elif str(type(object.__dict__[x])).startswith("<class"):
                    self.add(object.__dict__[x], object, index_call)

    def remove(self, object, parent):
        """Call this function from outside to remove object from parent

        Calls unindex() for every object under parent.

        """

        # Get all objects under parent.
        parents = [ elem for elem in self._eeindex[parent] if elem == object ]
        # For each of these objects remove them recursive.
        for elem in parents:
            self.unindex(elem, parent)
            self._eeindex[parent].remove(elem)  # remove "by hand"

    def unindex(self, object, parent):
        """Removes object and subobjects from parent"""
        # Check if the object exists under parent.
        if self._eeindex.get(object, None) is not None:
            # Delete recursive all childs of object
            for elem in [ bla for bla in self._eeindex[object] ]:
                self.unindex(elem, object)
            # If object under parent (by namespace) remove its namespace and
            # decrement _eenumber
            for parent_namespace in self._namespace[parent]:
                for object_namespace in self._namespace[object]:
                    if self._compare_namespace(object_namespace,
                                               parent_namespace):
                        self._namespace[object].remove(object_namespace)
                        self._eenumber[object] = self._eenumber[object] - 1
            # If _eenumber is zero (object does not exist in Collection
            # anymore), delete its _namespace, _eeindex and _eenumber and
            # remove it from collection
            if self._eenumber[object] == 0:
                del self._namespace[object]
                self.collection.remove(object)
                del self._eenumber[object]
                del self._eeindex[object]

    def all(self):
        """Return all objects without the RootObject"""
        return self.collection[1:]  # suppress the RootObject

    def root(self):
        """Return the RootObject"""
        return [ self.collection[0] ]

    def by_class(self, search_phrase, namespace=None):
        """Get all elements matching search_phrase in namespace"""
        return_list = []
        for elem in self.collection:
            # All elements which match the search_phrase
            if elem.__class__.__name__ == search_phrase:
                if namespace is None:
                    return_list.append(elem)
                else:   # Filter elements with namespace
                    for parent_namespace in namespace:
                        for object_namespace in self._namespace[elem]:
                            if self._compare_namespace(object_namespace,
                                                       parent_namespace):
                                return_list.append(elem)
        return return_list

    def by_attr(self, id, value):
        """Get all elements with the attribute id and the value value"""
        return [elem for elem in self.collection if hasattr(elem, id) and \
                (getattr(elem, id) == value)]

    def is_direct_child(self, child, parent):
        """Test if child is a direct child of parent"""
        for elem in self._eeindex.get(parent):
            if elem == child:
                return True
        return False

    def get_namespace(self, object):
        """Return the namespaces for a given object, else the root namespace"""
        return self._namespace.get(object,
                                   self._namespace.get(self.collection[0]))

    def get_value(self, id):
        """Returns the values for a given id"""
        return [getattr(elem, id) for elem in self.collection if hasattr(elem,
                                                                         id)]
