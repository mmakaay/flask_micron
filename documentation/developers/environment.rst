.. _dev_environment:

My development environment
==========================

In this section, I will describe my development environment. This is of
course strongly opinionated material and in no way the best environment
possible (since that would be your own environment, wouldn't it?)

The motivation for writing this section, is to *improve the future*, by:

  - preventing you from yelling "Why did nobybody tell me this years earlier?!"
  - giving me a good laugh, looking back at my old-school development environment.

.. _dev_python:

Python setup
------------

For development, I work on an Ubuntu Linux machine. Therefore, commands
that I talk about from here on, might require Ubuntu or another Debian-ish
distribution.

I make use of Python virtualenv for setting up my Python environment. This is
in line with the recommended way for working with Flask.  See the `Flask
Installation Documentation`_.

Some advantages are that the dependencies and utilities are not added to the
system-wide Python installation (keeping that environment clean) and that it
is possible to switch between different versions of Python.

For getting things up-and-running, I first install some tools in my global
Python installation::

    $ sudo apt-get install python python3 python-pip python-virtualenv

After this, I setup two virtual environments, one for Python 2 and one
for Python 3.

Python 2::

    $ virtualenv -p python venv2
    $ . venv3/bin/activate
    $ pip install Flask pylint sphinx
    $ deactivate

Python 3::

    $ virtualenv -p python3 venv3
    $ . venv2/bin/activate
    $ pip install Flask pylint sphinx
    $ deactivate

The packages that I install in my Python virtual environment are:

  - `Flask`_: Flask-Micron is built on top of the Flask package.
  - `Pylint`_: Strict checking of coding standards and possible errors in
    the code. Just like jsline, Pylint will hurt your feelings, but all
    for the greater good.
  - `Sphinx`_: The tool that is used to produce this documentation. 

.. _dev_testing: 

Testing
-------

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

To run all unit tests, you can use one of the following commands::

    $ python setup.py test
HIER HIER HIER TODO

The tests for Flask-Micron can be found in the tests/ directory. All
test files follow the file naming pattern `*_tests.py`. The discovery code
in `tests/__init__.py` will pickup the test files automatically when
performing a test run.

When writing tests, my tests directory uses the same directory structure
as the project that I am testing.





