.. _dev_testing: 

Testing
=======

Like every developer, I make loads of mistakes! Luckily, there's the
practice of Test Driven Development (TDD) to keep me on track and to
give me the courage to do drastic things to my code.

https://en.wikipedia.org/wiki/Test-driven_development

For writing my unit tests, I make use of the built-in Python unittest
framework. It follows the patterns that most testing frameworks follow
nowadays. I felt right at home when I started to use it, being familiar
with frameworks like JUnit (for Java), NUnit (for .NET) and PHPUnit
(for .. yeah, you guessed that one, right?)

https://docs.python.org/2/library/unittest.html

.. _dev_testing_running:

Running the tests
-----------------

To run all unit tests, you can use one of the following commands from the
root directory of the Flask-Micron project::

    $ python setup.py test

    $ python -m unittest discover

The first command is very verbose. It lists the results for every single
test that is executed. Although its output can be trimmed down quite a
bit by adding the ``-q`` option, I normally use the second command. That one
displays a clean and brief result::

    $ python -m unittest discover
    ......................................................................
    ................................
    ----------------------------------------------------------------------
    Ran 102 tests in 0.745s
    
    OK

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
One problem I have with this: I grow tired quickly when having to start a
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

.. _dev_testing_dirstructure:

Test directory structure
------------------------

The tests for Flask-Micron can be found in the ``tests/`` directory. All
test files follow the file naming pattern ``test_*.py``. By using this pattern,
``python -m unittest discover`` is able to automatically find all unit test
files in the project.

When writing tests, my ``tests/`` directory mirrors the directory structure
of the project that I am testing. This way, it is very easy to find the tests
that belong to a given script file in the project.

Here's a little project structure example, that shows the above in action::

    file1.py
    folder1/
        file2.py
        file3.py
    tests/
        test_file1.py
        folder1/
            test_file2.py
            test_file3.py

So the tests for ``folder1/file3.py`` can be found by convention in
``tests/folder1/test_file3.py``.

When you find that you are writing a lot of tests for a given script file,
then consider splitting up the tests for that file. Let's say that
``folder1/file2.py`` requires a lot of tests, then this is how I would split
up the test code::

    tests/
        folder1/
            file2/
                test_feature1.py
                test_feature2.py
                ...

In the Flask-Micron code, an example of this is are the tests for the
CSRF protection plugin, which can be found in ``tests/plugins/csrf/*``.
