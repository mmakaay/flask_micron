# -*- coding: utf-8 -*-
import unittest
from flask import Flask
from flask import json
from flask_micron import Micron
from flask_micron.plugins import csrf


def suite():
    test_loader = unittest.TestLoader()
    return test_loader.discover('tests')


class MicronTestCase(unittest.TestCase):

    def setUp(self):
        self.app = Flask('UnitTest')
        self.app.secret_key = 'Secret123'
        self.micron = Micron(self.app)

        self.appctx = self.app.app_context()
        self.appctx.push()

        self.reqctx = self.app.test_request_context()
        self.reqctx.push()

        self.client = self.app.test_client()

        self.csrf_token = None

    def tearDown(self):
        self.reqctx.pop()
        self.appctx.pop()

    def decorate(self, function, rule=None, **configuration):
        decorate = self.micron.method(rule, **configuration)
        return decorate(function)

    def editable_session(self):
        return self.client.session_transaction()

    def request(self, path, funcarg=None, **kvargs):
        headers = kvargs.setdefault('headers', {})
        if self.csrf_token and not csrf.CSRF_TOKEN_HEADER in headers:
            headers[csrf.CSRF_TOKEN_HEADER] = self.csrf_token

        response = self.client.post(path, data=json.dumps(funcarg), **kvargs)
        response.output = json.loads(response.data)

        if csrf.CSRF_TOKEN_HEADER in response.headers:
            self.csrf_token = response.headers[csrf.CSRF_TOKEN_HEADER]

        return response
