Flask-Micron
============

Introduction
------------
   
Flask-Micron is a method-oriented API framework for Python, focusing on
security and productivity. It is built on top of the excellent Flask
microframework.

The main goal for the project is to make it really simple for developers to
write microservice-style JSON webservices, honoring best practices for
security, and without having to pollute business logic code with HTTP
request handling knowledge.

Example code
------------

Here's the mandatory "Hello, world!" example for Flask-Micron::

    from flask import Flask
    from flask_micron import Micron
    app = Flask(__name__)
    micron = Micron(app)

    @micron.method()
    def hello_world(name='World'):
        return 'Hello, %s!' % name
        
What you can see here, is that Flask-Micron is a layer on top of Flask.
A decorator is provided, to embed Python functions in the Flask-Micron
request handling.

In the above code, Flask-Micron will setup a route ``/hello_world`` in
Flask. When a request comes in for that route, Flask-Micron will take
care of handling the request. One of the processing steps, is calling
the ``hello_world()`` function with the request input and capturing its
return value, which is returned to the requesting client.

Flask-Micron's main feature here, is that the function containing the
business logic for ``/hello_world`` does not require any boiler plate
code for stuff like taking a Flask request, loading the JSON input data
from it, normalizing the data and creating a Flask Response object
in JSON format.
