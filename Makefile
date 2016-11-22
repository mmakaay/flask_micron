.PHONY: docs

all: build_package

build_package: test, lint
	python setup.py build

test:
	python setup.py test

test-watch:
	watch -n 1 "python -m unittest"

lint:
	pylint --rcfile=.pylintrc-flask_micron flask_micron
	pylint --rcfile=.pylintrc-tests tests

develop:
	python setup.py develop

install:
	python setup.py install

docs:
	cd docs && make clean
	cd docs && make html

clean:
	find . -depth -type d -name __pycache__ -exec /bin/rm -fR {} \;
	find . -type f -name '*.pyc' -exec /bin/rm {} \;
	find . -type d -name '*.egg-info' -exec /bin/rm -fR {} \;
	find . -type d -name '*.egg' -exec /bin/rm -fR {} \;
	/bin/rm -fR build .eggs
	cd docs && make clean
