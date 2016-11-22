.. _design:

Design Decisions
================

In this section, some of the design choices for Flask-Micron will
be explained.

.. _design_method_oriented:

Method-oriented (SOAP-y), not Resource-oriented (REST, CRUD)
------------------------------------------------------------

Let's first state: I agree, there are applications for which REST is the
perfect back-end service style. For front-facing business applications
however (which Flask-Micron is targeting), I highly prefer using
method-oriented services.

A quick comparison of method-oriented::

  POST /user/create     { name: 'Bill Billderberg',
                          email: 'bill@example.com' }

  POST /user/get        { user_id: 1234 }

  POST /user/set_name   { user_id: 1234,
                          name: 'John Dorkingson' }

  POST /user/set_email  { user_id: 1234,
                          email: 'john@example.com' }

versus resource-oriented::

  PUT /user/1234        { name: 'Bill Billderberg',
                          email: 'bill@example.com' }

  GET /user/1234

  PATCH /user/1234      { name: 'John Dorkingson' }

  PATCH /user/1234      { email: 'john@example.com' }

  PATCH /user/1234      { name: 'John Dorkingson',
                          email: 'john@example.com' }

Using methods instead of resources has some advantages:

 - When designed with care, services that are composed out of methods will
   always be aware of the intent of a caller's request. A request is not
   about 'I want to update random data for a customer', but for example
   about 'I want to update the customer's e-mail address'.

 - Intent lives on in log messages. When reading the log messages for a
   given client, one can pretty much follow the business operations that
   this client has performed. An example comparison::

       GET /user/1234      POST /user/get
       PATCH /user/1234    POST /user/set_name
       PATCH /user/1234    POST /user/set_email

 - This becomes especially useful when an audit trail is required for an
   application: you don't only know what was changed, you also have a
   pretty clear idea about why it was done.

 - It is possible to apply the Single Responsibility Princple (SRP) and
   the Interface Seggregation Principle (ISP) to the service API's.
   We want those for internal code API's, don't we? So why not for our
   service API's as well?

 - One does not have to worry about a client accidentally sending more
   data than intended in a PATCH request, e.g. for a case where only a
   name change was intended, but the email property was sent along by
   accident as null, resetting the email address for the user unintendedly::

       PATCH /user/1234    { name: 'John Dough',
                             email: null }

.. _design_post_only:

POST-only
---------

Flask-Micron only accepts POST requests for various reasons.

* POST requests are slightly more secure than GET requests, in particular
  when the requests are using HTTP and not HTTPS.

  * With GET requests, one might leak important data via the URL. Yes, the
    same data would be exposed via the POST body, but that data wouln't
    be as visible for peeking Toms (looking over your shoulder, in your
    browser history, in proxy server logs, third party looking at your
    HTTP-Referer header, etc.)

  * POST requests are not cached by proxy servers, making it less likely
    for important data to end up there (of course, a malicious proxy
    would still be able to capture your POST data.)

* GET requests are very useful for retrieving resources for which the
  visitor must be able to create a bookmark. However, Flask-Micron is
  about writing API's, which consist of the back-end operations behind
  such page.

* For a method-oriented API, using only POST makes a lot of sense, because
  it greatly simplifies the way in which a client can talk to the API
  service. The focus is on "what method is being called" and not "what
  HTTP method fits the operation best".

**POST is not equal to security**

Contrary to popular belief, using JSON/POST instead of GET is not a good way
to for example prevent CSRF (Cross Site Request Forgery) attacks. Although
it is harder than forging GET requests, it is trivial to forge requests for
JSON/POST. To protect against this type of attack, see
:ref:`user_csrf-protection`.

Of course, when security is a concern (is it ever not?), some of the best
security measures that you can take, are:

* to stay up-to-date with `OWASP <https://www.owasp.org>`_ and ensure
  that your application code is secure;

* to use `HTTPS <https://en.wikipedia.org/wiki/HTTPS>`_ for exposing
  your website / API;

* to have your domain signed using `DNSsec <https://en.wikipedia.org/wiki/Domain_Name_System_Security_Extensions>`_.

.. _design_pluginarchitecture:

Plugin architecture
-------------------

When I started writing JSON webservices using `Flask`_, I quickly got bored
of writing the same kind of :ref:`boiler plate code <user_api-using-flask>`
for every function that I implemented. "Python decorators to the rescue!",
I thought.

I was partly right. I came up with a whole bunch of decorators that took
care of specific request handling tasks. I was able to use these with great
success on my functions. The code started to look like this::

    @app.route('/myfunc', methods=['POST'])
    @jsonify_output
    @check_authentication
    @validate_input
    @normalize_input
    @parse_json_input
    def myfunc(input_):
        ...
        ...
        return output

This is just a short version, since I had more decorators in place, but
you might already feel a bit uncomfortable with the direction I took
there. Some problems that I had with this approach:

* The decorators are executed "in reverse order". The thing is that the
  decorator closest to the function definition (``@parse_json_input``)
  wraps the function last, making it the first decorator to be executed
  when ``myfunc()`` is called.
* For the same reason, I had to be aware that the ``@app.route`` decorator 
  was always at the top of the list. When putting it further down the list,
  not all request handling decorators were on the function that was
  registered as a `Flask`_ route.
* The more decorators I got, the more difficult it became to make sure
  that they were used in the right order. For example, when switching the
  decorators ``@validate_input`` and ``@normalize_input``, the code
  would run, but validation would be performed on non-normalized data.
* When working on CSRF Protection with these decorators, I quickly ended
  up with multiple decorators because of the split operation (check for
  a valid token at the start, produce a new token at the end). So a
  single feature pushed me into using multiple decorators.
* All these decorators turned ``myfunc()`` into a function that knew all
  about HTTP request handling within a Flask environment. Therefore, I had
  to reproduce such environment (using the Flask test utilities) for every
  test that I wanted to implement. While this is fine for integration
  testing, it felt bad for unit testing.
* When creating a new decorator, I had to remember to put it on all
  functions that needed it (mostly: all of them).
* The decorator hell grew more complex with every new decorator that
  I added.

Eventually, the pain of these issues trumped the joy of the solution.
That was when I decided to create a single super-decorator, that would
take care of all my needs.

After a few painful iterations of my code (biggest stuggle: keeping the
code cleanly organized, honoring good design practices), I finally moved
towards the current hook-based :ref:`plugin system <user_plugins>`,
combined with the ``@micron.method`` decorator. This solved the above
issues for me:

* Because there is only a single decorator ``@micron.method``, I cannot
  accidentally put decorators in the wrong order.
* Flask-Micron executes the plugin hooks in a fixed, well-defined order.
  This takes away the risk of executing request handling phases in
  a different, wrong order.
* Since plugins can hook into multiple hooks, there is no problem in
  distributing a feature over multiple phases of the request handling.
* The ``@micron.method`` does register a wrapped version of the function
  with the Flask routing system. The function itself is left untouched,
  making it available for simple unit tests (note: Flask's ``@app.route()``
  decorator does the same.)
* Adding new features no longer increases complexity.

So in recap, what the plugin system did for me, was moving all of the
boiler plate code that I required for exposing my functions as API methods
into a predictable, simple and pluggable system. Keyword: headache-free!
