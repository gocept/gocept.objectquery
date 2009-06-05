# Copyright (c) 2007-2009 gocept gmbh & co. kg
# See also LICENSE.txt

import unittest

from zope.testing import doctest


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(doctest.DocTestSuite('gocept.objectquery.indexsupport'))
    suite.addTest(doctest.DocFileSuite(
        "interfaces.txt", "pathexpressions.txt",
        "indexsupport.txt", "querysupport.txt", "collection.txt",
        "processor.txt",
        optionflags=doctest.ELLIPSIS|doctest.NORMALIZE_WHITESPACE))
    return suite
