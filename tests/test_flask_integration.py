# -*- coding: utf-8 -*-
"""The tests in this module are used to make sure that Micron integrates
correctly with the Flask environment and its testing features.

The code does not extensively test all available Micron features, but
mainly checks if the plumbing isn't leaky.
"""

from tests import MicronTestCase


class Tests(MicronTestCase):

    def setUp(self):
        super(Tests, self).setUp()

        @self.micron.method()
        def greet(who='World'):
            return 'Hello, %s' % who

        @self.micron.method()
        def ping():
            return 'pong'

    def test_GivenMicronWrappedApp_PingReturnsPong(self):
        response = self.request('/ping')
        self.assertEqual('pong', response.output)

    def test_GivenMicronMethod_MethodGetIsNotAllowed(self):
        response = self.client.get('/ping')
        self.assertEqual('405 METHOD NOT ALLOWED', response.status)

    def test_GivenMicronMethod_ResponseIsReturned(self):
        response = self.request('/greet', "you")
        self.assertEqual('Hello, you', response.output)
