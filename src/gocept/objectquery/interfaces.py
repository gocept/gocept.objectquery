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

    def add(object_oid, parent_oid=None):
        """Add object_oid to indices (``under'' parent_oid)."""

    def delete(object_oid, parent_oid=None):
        """Delete object_oid from indices (``under'' parent_oid)."""

    def root():
        """Return the root object."""

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


class IClassIndex(Interface):
    """Map classnames to a list of objects of that class."""

    def insert(classname, obj):
        """Insert obj under classname into the index."""

    def delete(classname, obj):
        """Delete obj under classname from the index."""

    def get(classname):
        """Get all objects of the classname class."""

    def has_key(classname):
        """Return true if classname is in index, otherwise False."""

    def all():
        """Return all objects of all classes."""


class IAttributeIndex(Interface):
    """Map attribute names to a list of objects with that attribute."""

    def insert(attributename, obj):
        """Insert obj under attributename into the index."""

    def delete(attributename, obj):
        """Delete obj under attributename from the index."""

    def get(attributename):
        """Get all objects with the attribute attributename."""

    def has_key(attributename):
        """Return true if attributename is in index, otherwise False."""


class IStructureIndex(Interface):
    """Stores information about the relationship betwenn objects."""

    def insert(key, parent=None):
        """Insert key under parent (under root) into the index."""

    def delete(key, parent=None):
        """Delete key (under parent) from the index."""

    def is_child(key1, key2):
        """Check if key1 is direct successor of key2 (key1 child of key2)."""

    def is_successor(key1, key2):
        """Check is key1 is successor of key2 (key2 is reachable by key1)."""

    def get(key):
        """Return the paths for a given key."""

    def validate(key, pathlist):
        """Check if keys path is a part of paths inside pathlist."""

    def root():
        """Return the root object."""
