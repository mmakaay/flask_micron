from flask import Flask
from flask_micron import Micron

app = Flask(__name__)
micron = Micron(app)

@micron.method()
def hello_world(name='World'):
    return 'Hello, %s!' % name


if __name__ == '__main__':
    app.run(port=8888);
