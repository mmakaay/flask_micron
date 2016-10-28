all: build_package

build_package: lint
	python setup.py build

test:
	python setup.py test

test-watch:
	watch -n 1 "python setup.py test -q > /dev/null"

lint:
	pylint flask_micron

lint-watch:
	watch -n 10 "pylint flask_micron"

lint-test:
	pylint --rcfile=.pylintrc-test tests

develop:
	python setup.py develop

install:
	python setup.py install

clean:
	find . -depth -type d -name __pycache__ -exec /bin/rm -fR {} \;
	find . -type f -name '*.pyc' -exec /bin/rm {} \;
	find . -type d -name '*.egg-info' -exec /bin/rm -fR {} \;
	find . -type d -name '*.egg' -exec /bin/rm -fR {} \;
	/bin/rm -fR build .eggs

tmux:
	tmux new-session -d -s Flask-Micron
	tmux send-keys -t Flask-Micron:0 cd Space flask_micron C-m
	tmux split-window -h -p 47 -t Flask-Micron:0
	tmux send-keys -t Flask-Micron:0 make Space test-watch C-m
	tmux split-window -v -p 50 -t Flask-Micron:0
	tmux send-keys -t Flask-Micron:0 make Space lint-watch C-m
	tmux select-pane -t 0
	tmux split-window -v -p 50 -t Flask-Micron:0
	tmux send-keys -t Flask-Micron:0 cd Space tests C-m
	tmux select-pane -t 0
	tmux att -d -t Flask-Micron
