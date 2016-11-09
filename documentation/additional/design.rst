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

blah
