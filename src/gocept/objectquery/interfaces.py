# Copyright (c) 2007-2008 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

from zope.interface import Interface, Attribute

class IQueryParser(Interface):
    """ Parse an expression and return a queryplan.
    """

    def parse(expression):
        """ Parse an expression and return a queryplan.
        """

class IObjectCollection(Interface):
    """ Collects Index- and Querysupport for QueryProcessor.
    """

    def add(object_oid, parent_oid=None):
        """ Add object_oid to indices (``under'' parent_oid).
        """

    def delete(object_oid, parent_oid=None):
        """ Delete object_oid from indices (``under'' parent_oid).
        """

    def root():
        """ Return the root object.
        """

    def all():
        """ Return all objects.
        """

    def by_class(classname):
        """ Return a list of objects with match ``classname''.
        """

class IQueryProcessor(Interface):
    """ Processes a query to the collection and returns the result.
    """

    parser = Attribute("The parser which parses the query.")
    collection = Attribute ("The collection handling persistent objects.")

    def __call__(expression):
        """ Parse expression and determine the result.
        """
