install:
	pip install --upgrade pip &&\
		pip install -r requirements_ci.txt

test:
	pytest app/tests
	pytest --cov tests

black:
	black --line-length 79 --check --diff app
	black --line-length 79 --check --diff app/tests

isort:
	isort --check-only --diff --profile black --line-length 79 app

flake8:
	flake8 app
	flake8 app/tests
