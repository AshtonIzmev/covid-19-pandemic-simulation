init:
	pip install -r requirements.txt

test:
	 python -m tests.run

coverage:
	 coverage run -m pytest

report:
	 coverage report

codecov:
	 codecov --token=${CODECOV_TOKEN}

build:
	 python setup.py sdist bdist_wheel

clean:
	 python setup.py clean --all

check:
	 python -m twine check dist/*

testdeploy:
	  python -m twine upload --repository testpypi dist/*

deploy:
	  python -m twine upload dist/*

.PHONY: init test clean