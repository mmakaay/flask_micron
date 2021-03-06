.. _user_quickstart:

QuickStart
==========

In this chapter, I will explain how to get your first Flask-Micron app 
running. If you already familiar with writing JSON API's using Flask,
then you might want to jump directly to :ref:`user_api_using_flask_micron`.

.. _user_minimal_flask_app:

A minimal Flask application
---------------------------

Before explaining Flask-Micron, I first want to show you the minimal
`Flask`_ application from the `Flask Documentation`_::

    from flask import Flask
    app = Flask(__name__)

    @app.route('/')
    def hello_world():
        return 'Hello, World!'

For a full description of this code, check out the `Flask Quickstart
Documentation`_.  In short, this code links the root URL ('/') to the
hello_world() function. The application can be started using Flask::

    $ export FLASK_APP=hello.py
    $ python -m flask run
     * Running on http://127.0.0.1:5000

This is all that is needed to get the minimal example up and running.
Head over to `http://127.0.0.1:5000/ <http://127.0.0.1:5000/>`_ using your
web browser to see the function's greeting output.

.. note::

  Serving the app this way is meant for development purposes only.
  For information on deploying the app to a production environment, see the
  `Flask deployment documentation <http://flask.pocoo.org/docs/deploying>`_.

.. _user_api_using_flask:

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

Now imagine having to add extra features like authentication, authorization
and logging. You probably can foresee that things get out of hand fast.
This was my reason for starting the Flask-Micron project, with the ultimate
goal to bring back the implementation code for this kind of project to pure
business logic. 

.. _user_api_using_flask_micron:

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
function in a :any:`MicronMethod` object and registers this object with the
Flask app to be the handler for POST requests to ``/hello_world``.

From here on, the :any:`MicronMethod` will sit between Flask and the
function, taking care of tasks like reading the JSON request, normalizing
the request data, calling the wrapped function to get a result and
creating the JSON response message.

By making the :any:`MicronMethod` responsible for these tasks, we can now
focus on actual business logic when writing and testing the API functions::

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
  No tests were implemented for ``None`` and empty strings. The reason for
  this is that Flask-Micron normalizes input data by default: trailing and
  leading whitespace are stripped and empty strings are converted to None. When
  calling the wrapped function and the input is None, then the argument is
  omitted (by convention). Therefore, I omitted some tests, since the tested
  scenarios do not exist in practice.

.. _user_accessing_request_data:

Accessing request data
----------------------

Flask-Micron takes a very straight forward approach to handling request
data:

  - The function that provides the business logic can take a single argument
    or none at all. The argument can have a default value assigned to it.
  - Flask-Micron will pass the full deserialized and normalized JSON request
    data to the function, unless no data is provided.

These are the possible function patterns::

    @micron.method()
    def no_argument():
        return 'Hello, World!'

    @micron.method()
    def one_argument(who):
        return 'Hello, %s' % who

    @micron.method()
    def one_argument_with_default(who='World'):
        return 'Hello, %s!' % who

An exception is raised when:

  - ``no_argument()`` is called with request data.
  - ``one_argument()`` is called without request data.
  - a function would be defined with more than one argument.

What counts as 'without request data':

  - No payload at all in the request (an empty HTTP request body).
  - Just a JSON ``null`` value in the request (translates to ``None`` in Python).
  - Just an empty JSON string in the request (normalized to ``None``).
  - Just a JSON whitespace string in the request (normalized to ``None``).

When using any of the above when calling the example function
``one_argument_with_default()``, then Flask-Micron will call it without
any argument. As a result, the return value would be ``"Hello, World!"``.

.. _user_communicating_errors:

Communicating errors to API clients
-----------------------------------

Micron does not use a wide range of HTTP status codes to communicate
a response status to its clients. It only uses "200 OK" for successful
requests and "500 SERVER ERROR" for failed requests.

*Wow, that takes away a lot of expressiveness!!*

Not really... When a function raises an exception, Micron catches it and turns
turns the ugly beast into a frienly response message, containing information
about the exception that occurred. This way, a client that runs into an error
can get hold of a lot more information than what can normally be communicated
through an HTTP status code alone. If you have any experience with SOAP web
services, then you might understand what inspired me.

When you want to communicate an error, then the recommended way is to derive a
specific exception class from either ``MicronClientError`` or
``MicronServerError``. Provide at least a docstring that describes the error.
Simply raise your exception and Flask-Micron will take care of the rest for
you::

  from flask_micron import MicronClientError


  class FlaskIsHalfEmpty(MicronClientError):
      """Permission denied to pessimists, please consider the
      Flask half full before continuing.
      """

  @micron.method()
  def get_flask():
      if g.user.is_pessimistic:
          raise FlaskIsHalfEmpty()
      return "Here's your half full flask, sir!"

But what if you feel the need to provide more information about the error that
occurred? We can do that! Simply pass these details to the raised exception.
You can use any data structure that can be serialized into JSON here. The
information will be included in the response::

    raise FlaskIsHalfEmpty({
        "reason": "user is a pessimist",
        "source": "the mother told us"
    })

When the flask application has debugging enabled, then the response message
will also contain a backtrace of the error that occurred::

    app = Flask(__name__)
    app.debug = True

Here's an example response message that you would see with debugging enabled::

    {
      "caused_by": "client",
      "code": "FlaskIsHalfEmpty",
      "description": "Permission denied to pessimists, please consider " + \
                     "the Flask half full before continuing.",
      "details": {
        "reason": "user is a pessimist",
        "source": "the mother told us"
      },
      "trace": [
        "File \"...\", line ..., in ...",
        "File \"...\", line ..., in ...",
        "File \"...\", line ..., in ...",
        ...
      ]
    }

As you can see, ``caused_by``, ``code`` and ``description`` are directly
derived from the exception class that was used.

*"Okay, I agree, this is kinda useful. But what about standard exceptions?"*

Those are handled too! When you raise a non-MicronError exception or when you
don't catch an exception that is raised from a client library, then
Flask-Micron will catch it and turn it into an error response. The error code
``UnhandledException`` will be used::

    raise ValueError("I don't like it")

will result in::

    {
      "caused_by": "server",
      "code": "UnhandledException",
      "description": "During execution of a Micron method, an " + \
                     "exception was raised that was not handled " + \
                     "by the service.",
      "details": {
        "error_message": "I don't like it",
        "error_type": "ValueError"
      },
      "trace": [...]
    }

.. _user_configure_behavior:

Configuring Flask-Micron behavior
---------------------------------

As explained earlier, Flask-Micron automatically performs normalization on
string values in the input data. It can for example prevent needless
authentication failures when a user accidentally types a trailing space after
the username or password::

    {
        "credentials": {
            "username": "   johndoe   ",
            "password": "Udon'tKn0wm3! "
        },
        "token": "     "
    }

is normalized to::

    {
        "credentials": {
            "username": "johndoe",
            "password": "Udon'tKn0wm3!"
        },
        "token": None
    }

Sometimes you might require different behavior. No worries! All request
processing features in Flask-Micron are written as plugins and these
support :ref:`configuration <user_plugins_configurable>`. The plugin
that takes care of normalization provides the following configuration
options:

**normalize**: True/False (default = True)
    Whether or not to apply normalization to the request.

**strip_strings**: True/False (default = True)
    Whether or not to strip leading and trailing whitespace from strings.

**make_empty_strings_none**: True/False (default = True)
    Whether or not empty strings must be normalized to None.

Flask-Micron provides a configuration mechanism to tweak plugin behavior at
the level of the :any:`Micron` object and/or the level of the
``@micron.method()``. Configuration at the ``@micron.method()`` level
overrides configuration at the :any:`Micron` level::

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

  - Function ``hello_world()`` will get normalized input. Trailing and
    leading whitespace will not be stripped, but empty strings will be
    normalized to None.
  - Function ``good_bye_world()`` will get no normalized input at all, since
    it inherits the disabled normalization from the ``Micron`` object.

For information on the possible configuration options, take a look at the
documentation for the plugins that you use.
