from flask import Flask
from flask_micron import Micron

app = Flask(__name__)
app.secret_key = 'VerySecret###K3Y...shhht...!!!!'
micron = Micron(app)

@micron.method(csrf=False)
def hello_world(name='World'):
    return 'Hello, %s!' % name


if __name__ == '__main__':
    app.run(port=8888);
