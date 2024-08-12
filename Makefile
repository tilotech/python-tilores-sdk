all: setup test

setup:
	pip install .[test]

test:
	python -m unittest tests/*_test.py

