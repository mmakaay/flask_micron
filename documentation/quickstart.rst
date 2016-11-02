.. _quickstart:

QuickStart
==========

In this chapter, I will explain how to get your first Flask-Micron app 
running. If you already familiar with writing JSON API's using Flask,
then you might want to jump directly to :ref:`api-using-flask-micron`.

.. _minimal-flask-app

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

.. note::

  Serving the app this way is meant for development purposes only.
  For information on deploying the app to a production environment, see
  the Flask documentation.

.. _api-using-flask:

JSON API using Flask
--------------------

The marketing department has found that the 'Hello, World!' application is
going to be the next big hype. Therefore, it has to be opened up for all
kinds of clients (desktop, smart phones, smart tv, etc.) Additionally, there
is a big wish for making the greeting more personal. The greeting should only
say 'World', when no other name is known.

Based on this, the tech team worked out their design:
  - A JSON-based webservice, to facilitate integration with all platforms.
  - Clients POST a name JSON-serialized to the API.
  - The server strips leading and trailing whitespace from the name 
  - The server uses 'World' as the name, when no name is provided.
  - The server produces the result data, a friendly greeting.
  - The server sends the result data JSON-serialized to the client.

Okay, nothing to difficult! We've done this a million times before and Flask
Flask has everything on board to implement this new and ground breaking API::

    from flask import Flask, json, jsonify, request
    app = Flask(__name__)

    @app.route('/hello_world', methods=['POST'])
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
            response = client.post('/hello_world', data=request_data)
            result = json.loads(response.data)
            return result

        def test_GivenNoneOnInput_GreetingIsWordly(self):
            self.assertHelloWorldRequest(None, 'Hello, World!')

        def test_GivenEmptyStringOnInput_GreetingIsWordly(self):
            self.assertHelloWorldRequest('   ', 'Hello, World!')

        def test_GivenNameOnInput_GreetingIsPersonal(self):
            self.assertHelloWorldRequest('John', 'Hello, John!')

        def test_GivenNameWithWhitespaceOnInput_NameIsTrimmed(self):
            self.assertHelloWorldRequest('  Jacky\t\n ', 'Hello, Jacky!')

Even though this is a very basic level API method (simple input, simple
output, no authentication, no security checks, etc.), it is already noticeable
that both the implementation code and the test code are not extremely
straight forward.

The reason for this is the violation of the Single Reponsibility Principle
(SRP). The function and its tests cover more ground than the business logic
alone. The function has to know about Flask's request handling mechanisms,
while the tests have to use the Flask testing utilities to navigate the app,
as if it were already running in a web server.
To me, these unit tests are integration tests, since I have to work almost
the full stack in order to test my code.

Now imagine having to add extra features like :ref:`CSRF protection
<csrf-protection>`, authentication and logging, you probably can foresee
that things get out of hand fast. This is the reason that I started the
Flask-Micron project, with the ultimate goal to bring back the
implementation code for this kind of project to pure business logic. 

.. _api-using-flask-micron:

JSON API using Flask-Micron
---------------------------

Using Flask-Micron, we can greatly simplify the code from the previous section::

    from flask import Flask
    from flask_micron import Micron
    app = Flask(__name__)
    micron = Micron(app)

    @micron.method()
    def hello_world(name='World'):
        return 'Hello, %s!' % name

What happens here, is that ``@micron.method()`` wraps the ``hello_world()``
function in a MicronMethod object and registers this object with the Flask
app to be the handler for POST requests to ``/hello_world``.

From here on, the MicronMethod will sit between Flask and the function,
taking care of tasks like reading the JSON request, normalizing the request
data, performing security checks, calling the wrapped function to get a result
and creating the JSON response.

By making the MicronMethod responsible for these tasks, we can now focus on
actual business logic when writing and testing the API functions::

    import unittest
    from hello import hello_world

    class HelloWorldTest(unittest.TestCase):

        def test_GivenNameOnInput_GreetingIsPersonal(self):
            self.assertEqual('Hello, John!', hello_world('John'))

        def test_GivenNoNameOnInput_GreetingIsWordly(self):
            self.assertEqual('Hello, World!', hello_world())

These are actual unit tests instead of integration tests. The entrypoint for
the tests is ``hello_world()`` and not the Flask ``app``.

.. note::
  No tests were implemented for None and empty strings. The reason for this
  is that Flask-Micron normalizes input data by default: trailing and leading
  whitespace are stripped and empty strings are converted to None. When
  calling the wrapped function and the input is None, then the argument is
  omitted (by convention). Therefore, I omitted some tests, since the tested
  scenarios do not exist in practice.

.. _configuring-flask-micron-behavior

Configuring Flask-Micron behavior
---------------------------------

As explained in the previous section, Flask-Micron automatically performs
normalization on strings in the input data. This is a sane default. It can 
for example prevent needless authentication failures when a user accidentally
types a trailing space after the username or password.

Even though a sane default is used, sometimes you might require different
behavior. No worries! All processing features in Flask-Micron are written as
plugins and these plugins can be written in a configurable manner.
The normalization plugin supports the following configuration options:

normalize: True (default) or False
  Whether or not to apply normalization at all.

strip_strings: True (default) or False
  Whether or not leading and trailing whitespace must be stripped from
  string fields in the input data.

make_empty_strings_none: True (default) or False
  Whether or not string fields that contain an empty string must be
  normalized to None.

Flask-Micron provides a configuration mechanism to tweak plugin behavior at
the level of the ``Micron`` object and/or the level of the ``@micron.method()``.
Configuration at the ``@micron.method()`` level overrides configuration at the
``Micron`` level::

    from flask import Flask
    from flask_micron import Micron
    app = Flask(__name__)
    micron = Micron(app, normalize=False, strip_strings=False)

    @micron.method('/', normalize=True)
    def hello_world(name='World'):
        return 'Hello, %s!' % name

    @micron.method()
    def good_bye_world(name='World'):
        return 'Good bye, %s!' % name

Based on this configuration:

- Function ``hello_world()`` will get normalizated input. Trailing and
  leading whitespace will not be stripped, but empty strings will be
  normalized to None.
- Function ``good_bye_world()`` will get no normalized input at all, since
  it inherits the disabled normalization from the ``Micron`` object.

For information on the possible configuration options, take a look at the
documentation for the plugins that you use.

.. _csrf-protection:

Cross-Site Request Forgery (CSRF) protection
--------------------------------------------

Cross-Site Request Forgery (CSRF) is a type of attack where a user is
logged into site A, then visits site B which tells the browser
"Do this bad thing on site A". Without CSRF protection, site A actually
performs the "bad thing".

For more in depth info on CSRF, take a look at:
https://www.owasp.org/index.php/Cross-Site_Request_Forgery_(CSRF)

Because it is *very, very important* to protect your API's against this kind
of attack, Flask-Micron comes bundled with a CSRF protection plugin. This
plugin is enabled by default. This is something to beware of when trying to
talk to the web service from a client. You will have to play by the rules:

  1. All responses (also error responses) generated by Flask-Micron include
     a CSRF token in the HTTP header ``X-Micron-CSRF-Token``.

  2. Clients must take this token from the response header and include it
     in the HTTP header ``X-Micron-CSRF-Token`` on their next request.
     When no token is sent to Flask-Micron or an invalid token is sent,
     the request will be denied with an error.

I can hear you think: "But how do I get a token for my first request then?"
For that purpose, Flask-Micron automatically sets up a ``/ping`` method,
which does not check for a valid CSRF token. So the simple handshake from
above can be bootstrapped by issuing a ``/ping`` request from the client,
to get hold of a first token.

If you want to implement your own bootstrapping function, or if you want to
disable the CSRF protection module (which I advise strongly against), you
can make use of the ``csrf`` plugin configuration option::

    app = Flask(__name__)
    micron = Micron(app, csrf=False)

    @micron.method()
    def hello_world():
        return 'Hello, World!'

In this example, the ``hello_world()`` function is not CSRF-protected, because
the CSRF protection module has been fully disabled in the ``Micron``
constructor. Other functions in this API will also be unprotected. 

To disable CSRF protection for a single function, you can make use of the
``@micron.method()`` decorator configuration::

    app = Flask(__name__)
    micron = Micron(app)

    @micron.method(csrf=False)
    def give_me_a_token():
        return 'You will find your token in the headers'

    @micron.method()
    def hello_world():
        return 'Hello, World!'

In this example, the API provides the unprotected function
``give_me_a_token()``, that could be used (just like ``/ping``) for
bootstrapping the CSRF handshake cycle.

Below, a small client example that shows how one could obtain and use a
CSRF token using the http://python-requests.org Python library::

    import requests

    # Start a Session, to make the Flask session cookie work.
    s = requests.Session()

    # POST to /ping and fetch a fresh CSRF token from the headers.
    r = s.post('http://localhost:5000/ping')
    csrf_token = r.headers['X-Micron-CSRF-Token']

    # POST to /hello_world, including the CSRF token in the request headers.
    headers = {'X-Micron-CSRF-Token': csrf_token}
    r = s.post('http://localhost:5000/hello_world', headers=headers)

    print(r.text)

The output of this script is::

    "Hello, World!"
