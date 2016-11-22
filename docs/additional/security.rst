.. _security:

Security
========

When security is a concern (is it ever not?), then here are a few
important pointers:

* Stay up-to-date with `OWASP <https://www.owasp.org>`_ and ensure
  that your application code is secure (topics like
  `XSS <https://en.wikipedia.org/wiki/Cross-site_scripting>`_,
  `CSRF <https://en.wikipedia.org/wiki/Cross-site_request_forgery>`_ and
  `SQL Injection <https://en.wikipedia.org/wiki/SQL_injection>`_ should
  not sound mysterious!)

* Use `HTTPS <https://en.wikipedia.org/wiki/HTTPS>`_ for exposing
  your website / API;

* Have your domain signed using `DNSSEC
  <https://en.wikipedia.org/wiki/Domain_Name_System_Security_Extensions>`_.

Things that do not make your service / site secure:
  
  * POST-only requests
  * HTTPS
  * CSRF protection
  * XSS protection
  * SQL Injection protection
  * DNSSEC
  * Any other security measure (e.g. rate limiting)

Well, they all help of course! Important is that security is not a matter
of taking care of only a few of these. For security, an integral approach
is required. The cliché "the chain is as strong as its weakest link"
applies very much to security.
