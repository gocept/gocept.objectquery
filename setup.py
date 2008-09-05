# Copyright (c) 2007-2008 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$
"""Setup for gocept.objectquery package"""

import sys
import os.path

from setuptools import setup, find_packages

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

name = 'gocept.objectquery'

setup(
    name=name,
    version='0.1',
    url='http://www.python.org/pypi/'+name,
    license='ZPL 2.1',
    description='A framework for indexing and querying python objects',
    long_description = (read('README.txt')),
    author='Sebastian Wehrmann',
    author_email='sw@gocept.com',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    namespace_packages=['gocept',],
    include_package_data=True,
    install_requires=[
        'setuptools',
        'SimpleParse',
        'zope.interface',
        'zope.component',
        'ZODB3',
    ],
    zip_safe=False,
    )
