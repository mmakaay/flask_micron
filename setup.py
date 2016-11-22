"""
Flask-Micron
------------

A method-oriented microservice JSON framework, on top of the excellent
Flask package, focusing on security and productivity.

Basic features:

- Business logic is separated from request handling.
- Requests automatically use JSON for both input and output.
- Built-in security features like POST-only requests, CSRF protection,
  authentication and authorization

For more extensive feature information, see doc/FEATURES. 

Just like Flask, Flask-Micron is Fun
````````````````````````````````````

Save in hello.py:

.. code:: python

    from flask import Flask
    from flask_micron import Micron

    app = Flask(__name__)
    app.secret_key = 'some complex key for encrypting session data'
    micron = Micron(app)

    @micron.method()
    def hello(who="World"):
        return "Hello, %s", who

    if __name__ == "__main__":
        app.run()

And Easy to Setup
`````````````````

And run it:

.. code:: bash

    $ pip install Flask-Micron
    $ python hello.py 
     * Running on http://localhost:5000/

 Ready for production?
 `Read this first <http://flask.pocoo.org/docs/deploying/>`.
"""

import os
import re
from setuptools import find_packages
from setuptools import setup

def _get_version():
    path = os.path.abspath('.')
    pkginit = os.path.join(path, "flask_micron", "__init__.py")
    with open(pkginit, "r") as fh:
        for line in fh.readlines():
            m = re.match(r"^__version__\s*=\s*\"(.*)\"", line)  
            if (m is not None):
                return m.groups()[0]
    raise Exception("Unable to read version from %s" % pkginit)

setup(
    name='Flask-Micron',
    version=_get_version(),
    url='http://makaay.nl/flask-micron/',
    license='BSD',
    author='Maurice Makaay',
    author_email='maurice@makaay.nl',
    description='A JSON microservices framework on top of Flask',
    long_description=__doc__,
    packages=find_packages(exclude=('*tests', '*tests')),
    test_suite='tests.suite',
    zip_safe=False,
    include_package_data=True,
    platforms='any',
    install_requires=[
        'Flask'
    ],
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)
