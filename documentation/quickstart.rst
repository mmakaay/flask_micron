.. _quickstart:

QuickStart
==========

A minimal Flask application
---------------------------

Before starting with explaining Flask-Micron, first the minimal Flask
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

Based on this, the tech team worked out the design and came up with the idea
to provide a JSON-based webservice, which is easy to integrate with the
targeted platforms. The client simply has to POST the data to the API,
providing the input JSON serialized in the request body. The server will
respond with the result of the request JSON serialized in the response body.

Okay, nothing to difficult. Flask has everything on board to implement
the new API::

    from flask import Flask, json, jsonify
    app = Flask(__name__)

    @app.route('/', methods=['POST'])
    def hello_world():
        who = json.loads(request.data)
        if who is None or who.strip() == '':
            who = 'World'
        result = 'Hello, %s!' % who
        return jsonify(result)

And here are the accompanying unit tests::

    class HelloWorldTest(unittest.TestCase):

        def test_GivenNameOnInput_GreetingIsPersonal(self):
            client = app.test_client()
            response = client.post('/', data=json.dumps('John'))
            result = json.loads(response.data)
            self.assertEqual('Hello, John!', result)

        def test_GivenEmptyStringOnInput_GreetingIsWordly(self):
            client = app.test_client()
            response = client.post('/', data=json.dumps('   '))
            result = json.loads(response.data)
            self.assertEqual('Hello, World!', result)

        def test_GivenNoneOnInput_GreetingIsWordly(self):
            client = app.test_client()
            response = client.post('/', data=json.dumps(None))
            result = json.loads(response.data)
            self.assertEqual('Hello, World!', result)

Even though this is a very basic level API method (simple input, simple
output, not authentication, no security checks, etc), it is already noticeable
that both the implementation code and the test code are not extremely clear.

One reason for this is the violation of the Single Reponsibility Principle
(SRP). The function and the tests cover more ground than the business logic
alone. The function has to know about Flask's request handling mechanisms,
while the tests have to use the Flask test client to navigate the app.

Of course, refactoring can be applied to bring down the duplicated code
in the tests to a minimum. That wouldn't take away my feeling that this kind
of implementation could become unpleasant when working on big projects.
That is why I started Flask-Micron.
 
Now let's add Micron to this setup
----------------------------------

Using Micron, we can greatly simplify the code:

    from flask import Flask
    from flask_micron import Micron
    app = Flask(__name__)
    micron = Micron(app)

    @micron.method('/')
    def hello_world(who='World'):
        return 'Hello, %s!' % who

What happens here, is that @micron.method wraps the hello_world function
as a Micron method in the Flask app. When a client POSTs to '/', then Flask
will resolve the URL and calls the @micron.method wrapper. This wrapper
will take care of all interaction with Flask, JSON (de)serialization, security
checks, data normalization etc.
By providing these functionalities as part of the wrapper, we can now
focus on business logic when testing the API::

    class HelloWorldTest(unittest.TestCase):

        def test_GivenNameOnInput_GreetingIsPersonal(self):
            self.assertEqual('Hello, John!', hello_world('John'))

        def test_GivenNoNameOnInput_GreetingIsWordly(self):
            self.assertEqual('Hello, World!', hello_world())

Much simpler to write and actual unit tests instead of integration tests.
