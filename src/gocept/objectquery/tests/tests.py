# Copyright (c) 2007-2009 gocept gmbh & co. kg
# See also LICENSE.txt

import unittest
from zope.testing import doctest
import sw.objectinspection.testing
import zope.app.testing.functional

def test_suite():
#    suite = unittest.TestSuite()
#    suite.addTest(doctest.DocTestSuite('gocept.objectquery.indexsupport'))
    suite = zope.app.testing.functional.FunctionalDocFileSuite(
        "interfaces.txt",
        "pathexpressions.txt",
        "indexsupport.txt",
        "querysupport.txt",
        "collection.txt",
        "processor.txt",
    )
    suite.layer = sw.objectinspection.testing.FunctionalLayer
    return suite
