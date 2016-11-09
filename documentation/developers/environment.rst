.. _dev_environment:

My development environment
==========================

In this section, I will describe my development environment. This is of
course strongly opinionated material and in no way the best environment
possible (since that would be your own environment, wouldn't it?)

The motivation for writing this section, is to *improve the future*, by:

  - preventing you from yelling "Why did nobybody tell me this years earlier?!"
  - giving me a good laugh, looking back at my old-school development environment.

.. note:
  For development, I work on an Ubuntu Linux machine. Therefore, commands
  that I talk about from here on, might require Ubuntu or another Debian-ish
  distribution.

.. _dev_python:

Python setup
------------

I make use of Python virtualenv for setting up my Python environment. This is
in line with the recommended way for working with Flask.  See the `Flask
Installation Documentation`_.

Some advantages are that the dependencies and utilities are not added to the
system-wide Python installation (keeping that environment clean) and that it
is possible to switch between different versions of Python.

For getting things up-and-running, I first install some tools in my global
Python installation::

    $ sudo apt-get install python python3 python-pip python-virtualenv

After this, I setup two Python virtual environments, one for Python 2 and one
for Python 3. Although it is possible to create virtual environments directly
in the project source folder, I always create them in another folder.

Python 2::

    $ cd /where/you/want/to/create/the/virtualenv
    $ virtualenv -p python venv2
    $ . venv2/bin/activate
    (venv2) $ pip install Flask pylint sphinx
    (venv2) $ cd /the/flask_micron/sources
    (venv2) $ python setup.py develop
    (venv2) $ deactivate

Python 3::

    $ cd /where/you/want/to/create/the/virtualenv
    $ virtualenv -p python3 venv3
    $ . venv3/bin/activate
    (venv3) $ pip install Flask pylint sphinx
    (venv3) $ cd /the/flask_micron/sources
    (venv3) $ python setup.py develop
    (venv3) $ deactivate

The packages that I install in my Python virtual environment are:

  - `Flask`_: Flask-Micron is built on top of the Flask package.
  - `Pylint`_: Strict checking of coding standards and possible errors in
    the code. Just like jslint, Pylint will hurt your feelings, but all
    for the greater good.
  - `Sphinx`_: The tool that is used to produce this documentation. 

The command ``python setup.py develop`` installs Flask-Micron from the project
source directory into the virtual environment in development mode. This means
that the source code is not copied to, but linked from the virtual environment.
As a result, changes to the source code are available immediately in the virtual
environment.

.. _dev_shell:

Shell
-----

My shell of choice is Bash. There are many good things to say about bash,
but I will leave that up to the many fan sites.

http://www.gnu.org/software/bash/

The feature that I want to focus on here, is the ``alias`` command (supported
by other shells as well), which can be used to define new commands. Below are a
few useful ones that I use. 

``alias ls='ls --hide=*.pyc --hide=*.egg-info --hide=*.eggs --hide=__pycache__'``

This redefines the ``ls`` command ('list files in directory') to not show
the files and directories that Python might create and that are not part
of the source code. Those would normally clobber your output.

``alias pytest='python -m unittest'``

This alias brings down the number of keystrokes that I need to perform
to fire up my tests. See the :ref:`testing documentation
<dev_testing_running>` for info on this command. For example, the alias allows
me to start all unit tests in a directory by simply typing ``pytest``.
I also have an alias ``pywatch`` that I use for starting a continuous test
run in the working directory:

``alias pywatch='watch -n 1 "python -m unittest"'``

In general, any time when you find yourself getting bored of typing some
long command line over and over again, consider if you can create an alias
for it.

.. _dev_cvs:

Version control
---------------

For version control, I use Git. I have used some other solutions as well
in the past (e.g. RCS, CVS, Subversion, Mercurial and Bazaar), but Git is
the definite winner.

https://git-scm.com/

To have some direct feedback within my shell about the status of my
repository, I make use of ``bash-git-prompt``:

https://github.com/magicmonty/bash-git-prompt

.. _dev_editor:

Editor
------

For editing my code, I mostly use Vim.

http://www.vim.org

I use at least the following settings in my vim configuration ``~/.vimrc``::

    set ts=4
    set sw=4
    set expandtab
    set ai

This way indentation is automatic, using four spaces (not tabs).

For managing Vim plugins, I make use of Vundle:

https://github.com/VundleVim/Vundle.vim

The NRDTree plugin can be used to browse a directory tree within Vim.

https://github.com/scrooloose/nerdtree

CtrlP provides a fuzzy search interface, which helps me find files very
quickly from within Vim. For example the source for this documentation file
(``documentation/developers/environment.rst``) can be reached from anywhere in
the project, by hitting CTRL+P and typing ``env``.  That is already unique
enough for CtrlP to identify this file. I could also have typed ``docdevenv``.

http://ctrlpvim.github.io/ctrlp.vim

When you have ``ag`` installed (see :ref:`searching <dev_searching>`), then
I recommend adding the following to your ``~/.vimrc`` to let CtrlP
automatically ignore files from e.g. the ``.gitignore`` file::

    if executable('ag')
      let g:ctrlp_user_command = 'ag %s -l --nocolor -g ""'
    endif

.. _dev_terminal:

Terminal
--------

I am a big fan of ``tmux``, a terminal multiplexer like Gnu Screen, only
sooooo much better. I am a heavy user of tmux' panels (split screen).
I mostly have an editor running in one panel, while running a
:ref:`countinuous testing loop <dev_testing_continuous>` in another panel.
That allows me to quickly move forward using Test Driven Development (TDD,
highly recommended).

https://tmux.github.io/

.. _dev_searching:

Searching
---------

For searching through my source code, I don't use ``grep``. Instead I use
``ack``. One of its biggest features for me, is that it knows about
version control systems (VCS) and automatically skips VCS meta data files
and directories when traversing the source tree. This makes searching a lot
faster and the output will only contain matches from the actual source code.

http://beyondgrep.com/

Another search tool with similar grep-trumping features, but a lot faster
than ``ack`` is ``ag``. When starting with a grep replacement, then for now
I would recommend using ``ag`` instead of ``ack`` (if only for the very good
sales pitch of the ``ag`` author: "The command name is 33% shorter than ack,
and all keys are on the home row!")

https://github.com/ggreer/the_silver_searcher
