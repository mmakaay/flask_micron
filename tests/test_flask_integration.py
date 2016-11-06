"""The tests in this module are used to make sure that Micron integrates
correctly with the Flask environment and its testing features.

The code does not extensively test all available Micron features, but
mainly checks if the plumbing isn't leaky.
"""

from tests import MicronTestCase


class Tests(MicronTestCase):

    def setUp(self):
        super().setUp()

        @self.micron.method(csrf=True)
        def greet(who='World'):
            return 'Hello, %s' % who

    def test_GivenMicronWrappedApp_PingReturnsPong(self):
        response = self.request('/ping')
        self.assertEqual('pong', response.output)

    def test_GivenMicronMethod_MethodGetIsNotAllowed(self):
        response = self.client.get('/ping')
        self.assertEqual('405 METHOD NOT ALLOWED', response.status)

    def test_GivenMicronMethod_ResponseIsReturned(self):
        # This ping fetches a valid CSRF token.
        self.request('/ping')
        # This CSRF token is automatically included in this request
        # by self.request(), based on the ping from above.
        response = self.request('/greet', "you")
        self.assertEqual('Hello, you', response.output)
