from tests import MicronTestCase


class Tests(MicronTestCase):

    def test_InputAndOutput(self):
        """Checks if the input data is read from the request, if this
        data is normalized and if the response data is returned as JSON.
        """
        self.decorate(hello, csrf=False)
        response = self.request('/hello', "   John Doe   ")

        self.assertEqual(200, response.status_code)
        self.assertEqual('Hello, John Doe', response.output)
        self.assertEqual("application/json", response.content_type)

    def test_MethodCalling_WithMissingInput(self):
        """Checks the error that is returned when a method is called
        without input, while input is expected.
        """
        self.decorate(hello, csrf=False)
        response = self.request('/hello')

        self.assertEqual(500, response.status_code)
        self.assertEqual('client', response.output['caused_by'])
        self.assertEqual('MissingInput', response.output['code'])

    def test_MethodCalling_WithUnexpectedInput(self):
        """Checks the error that is returned when a method is called
        with input, while no input is expected.
        """
        self.decorate(say_it, csrf=False)
        response = self.request('/say_it', "Hah, surprise!")

        self.assertEqual(500, response.status_code)
        self.assertEqual('client', response.output['caused_by'])
        self.assertEqual('UnexpectedInput', response.output['code'])

    def test_MethodCalling_WithValidCsrfToken(self):
        """Checks a successful call, with CSRF checking active."""
        self.decorate(hello, csrf=True)
        self.request('/ping')
        response = self.request('/hello', "John Doe")
        self.assertEqual(200, response.status_code)
        self.assertEqual(u'Hello, John Doe', response.output)

    def test_NonMicronException(self):
        self.decorate(goodbye, csrf=False)
        response = self.request('/goodbye')

        self.assertEqual(500, response.status_code)
        self.assertEqual('server', response.output['caused_by'])
        self.assertEqual('UnhandledException', response.output['code'])
        self.assertEqual(
            'NotImplementedError',
            response.output['details']['error_type'])
        self.assertEqual(
            'This is what I call a failure',
            response.output['details']['error_message'])

    def test_WhenAppInDebugMode_TraceIsAddedForMicronException(self):
        self.app.debug = True
        self.decorate(hello, csrf=False)
        response = self.request('/hello')

        self.assertIsNotNone(response.output['trace'])
        self.assertTrue(isinstance(response.output['trace'], list))

    def test_WhenAppInDebugMode_TraceIsAddedForNonMicronException(self):
        self.app.debug = True
        self.decorate(goodbye, csrf=False)
        response = self.request('/goodbye')

        self.assertEqual('UnhandledException', response.output['code'])
        self.assertIsNotNone(response.output['trace'])
        self.assertTrue(isinstance(response.output['trace'], list))

    def test_WhenAppNotInDebugMode_NoTraceIsAddedForMicronException(self):
        self.decorate(hello, csrf=False)
        response = self.request('/hello')

        self.assertEqual('MissingInput', response.output['code'])
        self.assertIsNone(response.output['trace'])

    def test_WhenAppNotInDebugMode_NoTraceIsAddedForNonMicronException(self):
        self.decorate(goodbye, csrf=False)
        response = self.request('/goodbye')

        self.assertIsNone(response.output['trace'])


def hello(who):
    return "Hello, %s" % who


def say_it():
    return "it"


def goodbye():
    raise NotImplementedError('This is what I call a failure')
