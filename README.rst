Flask-Micron
============

Flask-Micron is a method-oriented API framework for Python, focusing on
security and productivity. It is built on top of the excellent `Flask
<http://flask.pocoo.org/>`_ microframework.

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
        
As you can see, Flask-Micron is a layer on top of Flask. A decorator
is provided, to add Python functions to the Flask-Micron request handling.

This code adds the route ``/hello_world`` to Flask. POST requests for that
route are handled by Flask-Micron, which takes care of:

  * reading, deserialzing and normalizing the JSON request body
  * calling the ``hello_world()`` function
  * creating a JSON response based on the function's return value.

Flask-Micron's main feature in action here, is that the function does not
require any boiler plate code to make all this work.

Running the example code
------------------------

To run the code, you can save the example code to ``hello.py`` and then
start a server for it.

    $ export FLASK_APP=hello.py
    $ flask run
     * Running on http://127.0.0.1:5000/

Another way would be to add the following code to ``hello.py``::

    if __name__ == '__main__':
        app.run()

and run the script::

    $ python hello.py
     * Running on http://127.0.0.1:5000/

Note: for production, this is not the best way to run your app, but
this is very useful for development purposes. For deployment in
production, take a look at the `Flask deployment documentation
<http://flask.pocoo.org/docs/deploying>`_.

Let's call it!
--------------

Now the app is running, we can send a POST request to it. Let's give this
baby a spin using the Curl tool::

    $ curl \
        -X POST \
        -H "Content-Type: application/json" \
        -d '"John Smith"' \
        http://127.0.0.1:5000/hello_world

Note that we use '"John Smith"' for the data here, which is the JSON
representation for a string. The response for this request contains
a JSON encoded greeting::

    "Hello, John Smith!"

Because a default value is provided for the argument in the function
definition, we can omit the data in the request::

    $ curl \
        -X POST \
        -H "Content-Type: application/json" \
        http://127.0.0.1:5000/hello_world

This result in::

    "Hello, World!"
