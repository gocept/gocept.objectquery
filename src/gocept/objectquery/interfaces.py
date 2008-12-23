# Copyright (c) 2007-2008 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

from zope.interface import Interface, Attribute


class IQueryParser(Interface):
    """Parse an expression and return a queryplan."""

    def parse(expression):
        """Parse an expression and return a queryplan."""


class IObjectCollection(Interface):
    """Collects Index- and Querysupport for QueryProcessor."""

    def index(obj):
        """Update indexes for given object."""

    def all():
        """Return all objects."""

    def by_class(classname):
        """Return a list of objects with match ``classname''."""


class IQueryProcessor(Interface):
    """Processes a query to the collection and returns the result."""

    parser = Attribute("The parser which parses the query.")
    collection = Attribute ("The collection handling persistent objects.")

    def __call__(expression):
        """Parse expression and determine the result."""


class IIndex(Interface):

    def index(obj):
        """Update the index for the given object."""

    def unindex(obj):
        """Remove the object from the index."""


class IClassIndex(IIndex):
    """Map classnames to a list of objects of that class."""

    def query(class_):
        """Return all objects that are instances of the given class or a subclass."""

    def all():
        """Return all objects of all classes."""
        # XXX Move this to the collection API.


class IAttributeIndex(IIndex):
    """Map attribute names to a list of objects with that attribute."""

    def query(attribute):
        """Return all objects that have the given attribute."""


class IStructureIndex(IIndex):
    """Stores information about the relationship between objects."""

    def is_child(oid1, oid2):
        """Check if key1 is direct successor of key2 (key1 child of key2)."""

    def is_successor(oid1, oid2):
        """Check is key1 is successor of key2 (key2 is reachable by key1)."""

    def get(oid):
        """Return all paths (from the root) to the object with the given OID."""

    def root():
        """Return the root object."""
        # XXX Move to collection
