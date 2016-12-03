# -*- coding: utf-8 -*-
import unittest
from flask import Flask
from flask import json
from flask_micron import Micron


def suite():
    test_loader = unittest.TestLoader()
    return test_loader.discover('tests')


class MicronTestCase(unittest.TestCase):

    def setUp(self):
        self.app = Flask('UnitTest')
        self.micron = Micron(self.app)

        self.appctx = self.app.app_context()
        self.appctx.push()

        self.reqctx = self.app.test_request_context()
        self.reqctx.push()

        self.client = self.app.test_client()

    def tearDown(self):
        self.reqctx.pop()
        self.appctx.pop()

    def decorate(self, function, rule=None, **configuration):
        decorate = self.micron.method(rule, **configuration)
        return decorate(function)

    def plugin(self, plugin_object):
        self.micron.plugins.add(plugin_object);

    def editable_session(self):
        return self.client.session_transaction()

    def request(self, path, funcarg=None, **kvargs):
        response = self.client.post(path, data=json.dumps(funcarg), **kvargs)
        response.output = json.loads(response.data)

        return response
