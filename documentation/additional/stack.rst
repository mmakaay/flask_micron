.. _stack:

Stack
=====

The "image" below shows an overview of the layers that are involved in
the Flask-Micron stack. Between the layers, you can find the interfaces
that are used for communication between the layers::

  +--------------------------------+
  |             Client             |
  +--------------------------------+
          |               ^
      HTTP POST     HTTP response
          v               | 
  +--------------------------------+
  |          Webserver             |
  +--------------------------------+
          |               ^
         WSGI           WSGI 
          v               |
  +--------------------------------+
  |       Werkzeug / Flask         |
  +--------------------------------+
          |               ^
       Request         Response
       Session         Session
          v               |
  +--------------------------------+
  |         Flask-Micron           |
  +--------------------------------+
  |       Flask-MicronMethod       |
  +--------------------------------+
  |      Flask-Micron Plugins      |
  +--------------------------------+
          |               ^
    function arg     return value
          v               |
  +--------------------------------+
  |    Business Logic Functions    |
  +--------------------------------+

An important Flask-Miron concept that is depicted here, is that the business
logic functions are separated from the HTTP request handling.
