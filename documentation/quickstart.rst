.. _quickstart:

QuickStart
==========

A minimal Flask application
---------------------------

Before explaining Flask-Micron, I first want to show you the minimal Flask
application from the `Flask Documentation`_::

    from flask import Flask
    app = Flask(__name__)

    @app.route('/')
    def hello_world():
        return 'Hello, World!'

For a full description of this code, check out Flask's documentation, it is
excellent. In short, this code links the root URL ('/') to the hello_world()
function. This application can be started using Flask::

    $ export FLASK_APP=hello.py
    $ python -m flask run
     * Running on http://127.0.0.1:5000

This is all that is needed to get the minimal example up and running.
Head over to `http://127.0.0.1:5000/ <http://127.0.0.1:5000/>`_ using your
web browser to see the function's greeting output.

JSON API, implemented using Flask
---------------------------------

Let's say the marketing department has found that hello_world() is going
to be the next big hype. Therefore, it has to be opened up for all kinds of
clients (desktop, phones, smart tv, etc.) Additionally, there is a big wish
for making the greeting more personal. The greeting should only say 'World',
when no other name is known.

Based on this, the tech team worked out their design:
  - A JSON-based webservice, to facilitate integration with all platforms.
  - Clients can POST a name JSON-serialized to the API.
  - The server will strip leading and trailing whitespace from the name 
  - The server will use 'World' as the name, when no name is provided.
  - The server produces the result data, a friendly greeting.
  - The server will send the result data JSON-serialized to the client.

Okay, nothing to difficult! Flask has everything on board to implement
this new and ground breaking API::

    from flask import Flask, json, jsonify, request
    app = Flask(__name__)

    @app.route('/', methods=['POST'])
    def hello_world():
        name = json.loads(request.data)
        if isinstance(name, str):
            name = name.strip()
        if name is None or name == '':
            name = 'World'
        result = 'Hello, %s!' % name
        return jsonify(result)

And here are the accompanying unit tests::

    import unittest
    from hello import app
    from flask import json, request

    class HelloWorldTest(unittest.TestCase):

        def assertHelloWorldRequest(self, arg, expected_result):
            client = app.test_client()
            request_data = json.dumps(arg)
            response = client.post('/', data=request_data)
            result = json.loads(response.data)
            return result

        def test_GivenNoneOnInput_GreetingIsWordly(self):
            self.assertHelloWorldRequest(None, 'Hello, World!')

        def test_GivenEmptyStringOnInput_GreetingIsWordly(self):
            self.assertHelloWorldRequest('   ', 'Hello, World!')

        def test_GivenNameOnInput_GreetingIsPersonal(self):
            self.assertHelloWorldRequest('John', 'Hello, John!')

        def test_GivenNameWithWhitespaceOnInput_NameIsTrimmed(self):
            self.assertHelloWorldRequest('   Jacky  \t\r\n ', 'Hello, Jacky!')


Even though this is a very basic level API method (simple input, simple
output, no authentication, no security checks, etc.), it is already noticeable
that both the implementation code and the test code are not extremely clear.

One reason for this is the violation of the Single Reponsibility Principle
(SRP). The function and its tests cover more ground than the business logic
alone. The function has to know about Flask's request handling mechanisms,
while the tests have to use the Flask testing utilities to navigate the app.
In fact, these unit tests are integration tests to me, since I have to work
almost the full stack in order to test my code.

Now imagine that we have to add extra features like CSRF protection,
authentication and logging, you probably can foresee that things get out of
hand fast. This is the reason that I started the Flask-Micron project, with
the ultimate goal to bring back the implementation code to pure business logic. 

JSON API, implemented using Flask-Micron
----------------------------------------

Using Flask-Micron, we can greatly simplify the code from the previous section::

    from flask import Flask
    from flask_micron import Micron
    app = Flask(__name__)
    micron = Micron(app)

    @micron.method('/')
    def hello_world(name='World'):
        return 'Hello, %s!' % name

What happens here, is that ``@micron.method`` wraps the hello_world function
as a Micron method and registers it with the Flask app to be linked to the
root url. When a client POSTs to '/', then Flask will resolve the URL and
calls ``hello_world()`` via the ``@micron.method`` wrapper.

From here on, the wrapper will take care of all interaction with Flask,
JSON (de)serialization, security checks, data normalization etc.
By making the wrapper responsible for these tasks, we can now focus on
actual business logic when testing (and writing) the API::

    import unittest
    from hello import hello_world

    class HelloWorldTest(unittest.TestCase):

        def test_GivenNameOnInput_GreetingIsPersonal(self):
            self.assertEqual('Hello, John!', hello_world('John'))

        def test_GivenNoNameOnInput_GreetingIsWordly(self):
            self.assertEqual('Hello, World!', hello_world())

Much simpler to write and actual unit tests instead of integration tests:
these are tests against ``hello_world()`` and not against ``app``.

*Note: no tests were implemented for None and empty strings. The reason for this
is that Flask-Micron normalizes input data by default: trailing and leading
whitespace are stripped and empty strings are converted to None. When calling
a function and the input is None, then the argument is omitted (by convention).
For those reasons, I didn't write specific tests for None and empty strings.
The @micron.method wrapper arranges that those scenario's won't occur
in practice.*
