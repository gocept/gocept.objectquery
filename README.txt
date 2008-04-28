===========
ObjectQuery
===========

ObjectQuery is licensed under ZPL 2.1

Copyright 2007-2008 by "gocept gmbh & co. kg":http://www.gocept.com

About
-----

ObjectQuery enables you to query for persistent objects (e.g. objects in the
ZODB). This is done with a XPath-like language named Regular Path Expressions
(RPE). Please refer src/gocept/objectquery/pathexpressions.txt for information
about the syntax. ObjectQuery also comes with indexstructures for performance
reasons.

It uses SimpleParse to parse the RPE-query.

Installation
------------

ObjectQuery is shipped as a python egg. You can install it using buildout.

On UNIX-like systems, do:

  ~/oq$ python bootstrap.py
  ~/oq$ bin/buildout

On Windows, open a command prompt and type:

  C:\>python \path_to_oq\bootstrap.py
  C:\>\path_to_oq\bin\buildout.exe

The buildout-process installs all needed packages (e.g. SimpleParse) from the
CheeseShop. Be sure that your internet connection is up and running.

After installation you may run the tests to verify, that everything works:

  UNIX: ~/oq: bin/test
  WIN:  C:\>\path_to_oq\bin\test.exe

You will find the sources under src/gocept/objectquery/*.py. The doctests are
located under src/gocept/objectquery/*.txt. You should read them for further
information about the modules.

Usage
-----

You may use the debug-promt (bin/debug) which is a regular python shell with
all needed packages installed. Details in using the ObjectQuery is explained
in src/gocept/objectquery/processor.txt.
