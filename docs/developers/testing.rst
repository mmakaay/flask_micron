.. _dev_testing: 

Testing
=======

Like every developer, I make loads of mistakes! Luckily, there's the
practice of Test Driven Development (TDD) to keep me on track and to give me
the courage to do drastic things to my code.

https://en.wikipedia.org/wiki/Test-driven_development

For writing my unit tests, I make use of the built-in Python unittest
framework. It follows the patterns that most testing frameworks follow
nowadays. I felt right at home when I started to use it, being familiar with
frameworks like JUnit (for Java), NUnit (for .NET) and PHPUnit (for .. yeah,
you guessed that one, right?)

https://docs.python.org/2/library/unittest.html

.. _dev_testing_running:

Running the tests
-----------------

To run all unit tests, you can use one of the following commands from the
root directory of the Flask-Micron project::

    $ python setup.py test

    $ python -m unittest discover

The first command is very verbose. It lists the results for every single
test that is executed. Although its output can be trimmed down quite a bit
by adding the ``-q`` option, I normally use the second command. That one
displays a clean and brief result::

    $ python -m unittest discover
    ......................................................................
    ................................
    ----------------------------------------------------------------------
    Ran 102 tests in 0.745s
    
    OK

.. note::
    When working with Python 3, 'discover' can be omitted from the command
    line: ``python -m unittest``

To run all tests contained by a testing subdirectory, the second command
from above is very useful as well. For example, to run all tests for the
CSRF protection plugin, you can do::

    $ cd tests/plugins/csrf
    $ python -m unittest discover
    .....................
    ----------------------------------------------------------------------
    Ran 21 tests in 0.321s

    OK

It is also possible to run the tests from a single test file. Let's say you
want to run the tests from ``tests/test_micron.py``, then you can do::

    $ python -m unittest tests/test_micron.py
    .....
    ----------------------------------------------------------------------
    Ran 5 tests in 0.087s
    
    OK

.. _dev_testing_continuous:

Continuous testing
------------------

When performing TDD-style development, one has to run unit tests very often,
since it is an active part of the development cycle "red, green, refactor".
One issue I have with this: I grow tired quickly when having to start a
test run manually for every step in this cycle.

Luckily, I work on a UNIX system, where most of the time there is a right
tool for a right job. In this case, the right tool is called ``watch``.  This
tool can be instructed to start a command on regular intervals and show its
output on screen. Exactly what we need here::

    $ watch -n 1 "python -m unittest discover"

By editing my code in one terminal, while having this command running in
another, I can keep an eye on the results of my unittest while writing my
code. 

For more information on ``watch``, take a look at its manual page::

    $ man watch

.. _dev_testing_tox:

Testing against multiple environments
-------------------------------------

`Tox <https://tox.readthedocs.io/>`_ is a virtualenv-based test tool,
which I use to check if Flask-Micron installs and runs correctly with
multiple versions of Python. The following commands are used to setup
the requirements for running Tox on my development machine::

    $ sudo apt-get install \
        python \
        python3 \
        pypy \
        python-pip \
        python-virtualenv
    $ pip install tox

This sets up three different versions of Python and Tox.  After doing this,
the ``tox`` command can be run to perform tests against the installed
environments (as defined in ``tox.ini``). When all goes well, it will look
somewhat likt this::

    $ tox
    ...
    (test output)
    ...
    py2: commands succeeded
    py3: commands succeeded
    pypy: commands succeeded
    congratulations :)

.. _dev_testing_dirstructure:

Test directory structure
------------------------

The tests for Flask-Micron can be found in the ``tests/`` directory. All
test files follow the file naming pattern ``test_*.py``. By using this pattern,
``python -m unittest discover`` is able to automatically find all unit test
files in the project.

PyLint
------

I let PyLint check all my code. PyLint is a tool that checks for code that
does not follow the Python coding standards and for common code smells that
could indicate bugs.

The tests and the flask_micron package have their own PyLint configuration
file (``.pylinerc-tests`` and ``.pylintrc-flask_micron`` respectively).
I do not use a single file for both, because I use slightly different
rules for package code and testing code.

To let PyLint check the package and the tests, run the following commands
from the Flask-Micron source code directory::

    $ pylint --rcfile=.pylintrc-flask_micron flask_micron
    $ pylint --rcfile=.pylintrc-tests tests
