# -*- coding: utf-8 -*-
"""
    jQuery Example
    ~~~~~~~~~~~~~~

    A simple application that shows how Flask-Micron and jQuery get along.
    This example is adapted from the Flask example with the same name.

    :copyright: (c) 2016 by Stichting Fiber Overal
    :license: BSD, see LICENSE for more details.
"""
from flask import Flask, render_template
from flask_micron import Micron

app = Flask(__name__)
app.secret_key = 'SimpleKeySinceThisIsJustADemo'
micron = Micron(app)


@micron.method('/_add_numbers', csrf=False)
def add_numbers(numbers):
    """Sum a list of numbers server side, ridiculous but well..."""
    total = 0
    for number in numbers:
        try:
            total = total + float(number)
        except ValueError:
            pass
        except TypeError:
            pass
    return total


@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run()
