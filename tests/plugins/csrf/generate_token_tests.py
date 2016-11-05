import unittest
from flask_micron.plugins import csrf


class Tests(unittest.TestCase):

    def test_GeneratorGeneratesTokens(self):
        """Just a basic test to see if we wired up everything correctly
        and that we are actually generating unique tokens.
        """
        a_bunch = set()
        for i in range(0, 10):
            a_bunch.add(csrf._generate_token())
        self.assertEqual(10, len(a_bunch))
