# project metadata
NAME := $(shell python3 setup.py --name)
FULLNAME := $(shell python3 setup.py --fullname)
VERSION := $(shell python3 setup.py --version)
BUILD := $(shell git rev-parse --short HEAD)

.PHONY: info clean dist docs

info: ## project info
	@echo $(FULLNAME) at $(BUILD)

clean: clean-build clean-pyc clean-log clean-test ## remove all build, test, coverage and Python artifacts

clean-build: ## remove build artifacts
	rm -fr build/
	rm -fr dist/
	rm -fr .eggs/
	find . -name '*.egg-info' -exec rm -fr {} +
	find . -name '*.egg' -exec rm -f {} +

clean-pyc: ## remove Python file artifacts
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -fr {} +

clean-log: ## remove log artifacts
	find . -name '*.log' -exec rm -f {} +

clean-test: ## remove test and coverage artifacts
	rm -fr .tox/
	rm -f .coverage
	rm -fr coverage
	rm -fr htmlcov/
	rm -fr .pytest_cache

format: ## format code with black and isort
	find . -name '*.py' -type f -not -path "*/pb/*" -not -path "*/data/*" -exec autoflake -i --remove-all-unused-imports --ignore-init-module-imports {} +
	find . -name '*.py' -type f -not -path "*/pb/*" -not -path "*/data/*" -exec black {} +
	find . -name '*.py' -type f -not -path "*/pb/*" -not -path "*/data/*" -exec isort {} +

docs: ## format docs
	doctoc --gitlab README.md

install: ## install the package to the active Python's site-packages
	pip3 install . -U --no-index

uninstall: ## uninstall the package
	pip3 uninstall $(NAME)

dist: clean ## package
	python3 setup.py sdist bdist_wheel

upload: dist # upload the package to pypi
	twine upload dist/*
