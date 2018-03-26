TOX := $(shell which tox || which ~/.virtualenvs/tox/bin/tox)

all: docs lint test dist

help:
	@echo "Usage: make [TARGETS]"
	@echo
	@echo "Targets:"
	@echo "  all            Shortcut for targets: docs lint test dist. (default)"
	@echo "  clean          Remove all temporary artifacts."
	@echo "  dist           Create source and binary wheel distribution."
	@echo "  docs           Generate documentation."
	@echo "  docswatch      Generate documentation and watch for changes."
	@echo "  lint           Perform PEP8 style check, run PyFlakes, and run McCabe"
	@echo "                 complexity metrics."
	@echo "  test           Run all tests on each supported interpreter."
	@echo "  test-unit      Run non-integration tests on each supported interpreter."

check-tox:
ifeq ($(TOX),)
	$(error tox (https://tox.readthedocs.io/) needs to be installed, e.g. install via "pip install tox")
endif

clean:
	rm -rf .cache .coverage .coverage.* .tox build dist docs/build *.egg-info htmlcov coverage.xml

dist:
	python setup.py sdist bdist_wheel

docs: check-tox
	$(TOX) -e docs

docswatch: check-tox
	$(TOX) -e docs -- livehtml

lint: check-tox
	$(TOX) -e lint

publish: clean dist
	twine upload dist/*

test: check-tox
	$(TOX)

test-unit: check-tox
	PYTEST_ADDOPTS='-m "not integration"' $(TOX)

.PHONY: help check-tox clean dist docs docswatch lint publish test test-unit
