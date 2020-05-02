init:
	pip install -r requirements.txt

test:
	 python -m tests.run

.PHONY: init test