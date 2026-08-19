PYTHON ?= python

init:
	$(PYTHON) -m pip install -r requirements.txt

init-dev:
	$(PYTHON) -m pip install -r requirements-dev.txt

lint:
	$(PYTHON) -m ruff check .

format:
	$(PYTHON) -m ruff check . --fix

test:
	$(PYTHON) -m pytest

coverage:
	$(PYTHON) -m pytest --cov --cov-report=xml --cov-report=term

build:
	$(PYTHON) -m build

check:
	$(PYTHON) -m twine check dist/*

clean:
	rm -rf build dist *.egg-info .pytest_cache .coverage coverage.xml
	find . -name __pycache__ -type d -prune -exec rm -rf {} +

testdeploy: build check
	$(PYTHON) -m twine upload --repository testpypi dist/*

deploy: build check
	$(PYTHON) -m twine upload dist/*

.PHONY: init init-dev lint format test coverage build check clean testdeploy deploy
