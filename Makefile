init:
	pip install -r requirements.txt

test:
	 python -m tests.main_test

.PHONY: init test