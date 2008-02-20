# Copyright (c) 2007 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

import unittest

from zope.testing import doctest


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(doctest.DocFileSuite("indexsupport.txt",
    #                                   "collection.txt",
    #                                   "processor.txt",
    #                                   "pathexpressions.txt",
                                       optionflags=doctest.ELLIPSIS))
    return suite
