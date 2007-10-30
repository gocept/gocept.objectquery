# Copyright (c) 2007 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

import types
import gocept.objectquery.indexsupport

class ObjectCollection(object):
    """ ObjectCollection provides functionallity to QueryProcessor.

        It helps to query for objects and bounds the indexes from
        IndexSupport.
    """

    def __init__(self):
        """ Initialize Indizes. """
        # ElementIndex is used the way as described within IndexSupport
        self.__element_index = gocept.objectquery.indexsupport.ElementIndex()
        # PathIndex objects are collected within a dictionary with objects as
        # keys. Because objects may occur multiple times (and therefore need
        # more than one PathIndex), they are kept inside a list.
        # e.g. {<object...>: [<PathIndex ...with path '...'>, <PathIndex...>],
        #       <object...>: [<PathIndex ...with path '...'>]}
        self.__path_index = {}
        self.__cycle_support = gocept.objectquery.indexsupport.CycleSupport()
        self.__oid = gocept.objectquery.indexsupport.ObjectToId()

    def __add_object(self, object, parent):
        """ Adds ``object`` to ObjectCollection under ``parent``. """
        # make IDs
        object = self.__oid.obj2id(object)
        if parent is not None:
            parent = self.__oid.obj2id(parent)
        # Test if adding would result in object tree with *cycles*
        if not self.__cycle_support.check_for_cycles(
                                [object], parent):
            raise ValueError("Cannot add object %s. Cycle detected." %
                             self.__oid.id2obj(object))
        self.__cycle_support.add(object, parent)
        # If the object hasn't been added before, add the PathIndex tuple.
        if self.__path_index.get(object, None) is None:
            self.__path_index[object] = []
        # Here we add the object as root (raises exception if root already
        # exists
        if parent is None:
            self.__element_index.add(object)
            self.__path_index[object].append(
                                gocept.objectquery.indexsupport.PathIndex())
        # Add the object under parent
        else:
            self.__element_index.add(object, parent)
            # There can be more than one parent PathIndex, so we have to add
            # object under each one
            for par in self.__path_index[parent]:
                self.__path_index[object].append(par.bear(object))

    def __check_path_index(self, pi_child_list, pi_parent_list):
        """ Checks if child is in parent. No direct child match!

            We get lists here because objects may occur under different
            parents. Returns False if there is no child in list which is under
            one of the parents in list.
        """
        for child in pi_child_list:
            for parent in pi_parent_list:
                if child in parent:
                    return True
        return False

    def __get_descendant_objects(self, object):
        """ Look through an object to find following objects. """

        # TODO: - add the 'path' to a following object (e.g. list 'xy')

        returnlist = []
        # Look through objects __dict__ for classes and tupels or the like.
        if hasattr(object, "__dict__"):
            for x in object.__dict__.keys():
                # Is x a list or a tuple, then traverse it and add the
                # content.
                if isinstance(object.__dict__[x],
                              types.ListType) or isinstance(object.__dict__[x],
                                                            types.TupleType):
                    for y in object.__dict__[x]:
                        returnlist.append(y)
                # Is x a dictionary, then traverse it and add the content.
                elif isinstance(object.__dict__[x], types.DictType):
                    for y in object.__dict__[x].keys():
                        returnlist.append(y)
                # Is x another class, then add it.
                elif str(type(object.__dict__[x])).startswith("<class"):
                    returnlist.append(object.__dict__[x])
        return returnlist

    def __unindex(self, object, parent=None):
        """ Recurive deletion of PathIndex objects. """
        if parent is None:
            parent = self.root()
        parent = self.__oid.obj2id(parent)
        object = self.__oid.obj2id(object)

        # Get the childs in ObjectCollection
        childs = self.__element_index.list(object)[:]
        for elem in childs:
            self.__unindex(self.__oid.id2obj(elem), self.__oid.id2obj(object))
        # Deletion of PathIndex objects. It looks through all parent
        # PathIndexes and deletes all child PathIndexes, which are direct
        # childs of the parent ones.
        # It is possible, that PathIndexes are already removed but do exist in
        # __element_index, so we have to test, if __path__index[object] does
        # exist.
        if self.__path_index.get(parent, None) is not None:
            # pi is one parent PathIndex object
            for pi in self.__path_index[parent]:
                if self.__path_index.get(object, None) is not None:
                    objlist = self.__path_index[object][:]
                    # obj is one child PathIndex object
                    for obj in objlist:
                        if pi.is_direct_parent(obj):
                            pi.delete(obj)  # PathIndex method
                            # remove it from the dict-list
                            self.__path_index[object].remove(obj)
                    # if the dict-list is empty, remove it from dict
                    if self.__path_index[object] == []:
                        del self.__path_index[object]


    def add(self, object, parent=None):
        """ Main add method.

            Calls itself to sub-objects and __add_object for instantiated
            classes.
        """

        # TODO: - add more objects than instantiated classes only

        desclist = self.__get_descendant_objects(object)
        # add instantiated classes (see TODO)
        if str(type(object)).startswith("<class"):
            self.__add_object(object, parent)
        for elem in desclist:
            # ensure that multiple occurences of subtrees are not added
            # multiple times
            # this is done by:
            #   - first not descending into objects, which are already added
            #     (because their sub-tree already exists in Collection)
            #     -> if statement
            #   - secound only adding objects if their number in desclist is
            #     not equal to their number in ObjectCollection
            #     -> elif statement
            if self.__oid.obj2id(elem) not in self.__element_index.list(
                                                    self.__oid.obj2id(object)):
                self.add(elem, object)
            elif len([e for e in desclist if e == elem]) !=\
                    len([e for e in
                         self.__element_index.list(self.__oid.obj2id(object))\
                             if self.__oid.id2obj(e) == elem]):
                self.__add_object(elem, object)

    def remove(self, object, parent=None):
        """ Main remove method.

            Calls ``__unindex`` to recursive remove the PathIndex objects from
            dictionary. The calls ``__element_index.delete()`` which deletes
            the element_indexes.
        """

        # Order is important! __unindex needs __element_index for removing
        self.__unindex(object, parent)
        self.__element_index.delete(self.__oid.obj2id(object),
                                    self.__oid.obj2id(parent))
        self.__cycle_support.delete(self.__oid.obj2id(object),
                                    self.__oid.obj2id(parent))

    def move(self, object, parent, target):
        """ Main move method.

            Calls the ElementIndex move method and for each child and parent
            the PathIndex move method.
        """

        object = self.__oid.obj2id(object)
        parent = self.__oid.obj2id(parent)
        target = self.__oid.obj2id(target)
        self.__element_index.move(object, parent, target)
        self.__cycle_support.move(object, parent, target)
        # Generate a move list
        movelist = []
        for child in self.__path_index[object]:
            for par in self.__path_index[parent]:
                if child in par:
                    movelist.append((par, child))
        # move every object in movelist under each target object
        for child in movelist:
            for newpar in self.__path_index[target]:
                child[0].move(child[1], newpar)


    def all(self):
        """ Return a list of all objects within the ObjectCollection. """
        return [self.__oid.id2obj(elem) for elem in\
                self.__element_index.rlist()]

    def by_class(self, name, pathindex=None):
        """ Return a list of objects which match ``name`` under ``pathindex``.

            name is a string which matches the classname. pathindex is a list
            of PathIndex objects.
        """

        # TODO: - what matches name if we don't only add instantiates classes

        if pathindex is None:
            pathindex = self.__path_index[self.__oid.obj2id(self.root())]
        return [e for e in self.all() if (e.__class__.__name__ == name) and \
                    self.__check_path_index(self.__path_index.get(
                                        self.__oid.obj2id(e), []), pathindex)]

    def by_attr(self, id, value):
        """ Return a list of objects which match attribute id and value. """

        return [elem for elem in self.all() if hasattr(elem, id) and \
                                (getattr(elem, id) == value)]

    def get_pathindex(self, object=None):
        """ Return the list of PathIndexes for object. """

        if object is None:
            object = self.root()
        return self.__path_index[self.__oid.obj2id(object)]

    def is_direct_child(self, child, parent, pathindex=None):
        """ Matches if child is a direct child of parent within a given
        pathindex. """
        child = self.__oid.obj2id(child)
        parent = self.__oid.obj2id(parent)
        if pathindex is None:
            pathindex = self.__path_index[parent]
        if child in self.__element_index.list(parent):
            for child_pathindex in self.__path_index[child]:
                for parent_pathindex in pathindex:
                    if child_pathindex in parent_pathindex:
                        return True
        return False

    def root(self):
        """ Return the root object. """
        return self.__oid.id2obj(self.__element_index.root())
