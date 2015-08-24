TOX := $(shell which detox || which tox || which ~/.virtualenvs/tox/bin/tox)

all: docs lint test dist

help:
	@echo "Usage: make [TARGETS]"
	@echo
	@echo "Targets:"
	@echo "  all            Shortcut for targets: docs lint test dist. (default)"
	@echo "  clean          Remove all temporary artifacts."
	@echo "  dist           Create source and binary wheel distribution."
	@echo "  docs           Generate documentation."
	@echo "  lint           Perform PEP8 style check, run PyFlakes, and run McCabe"
	@echo "                 complexity metrics."
	@echo "  test           Run test commands on each supported interpreter."

check-tox:
ifeq ($(TOX),)
	$(error tox (http://tox.readthedocs.org/) needs to be installed, e.g. install via "pip install tox")
endif

clean:
	rm -rf .tox artifacts build dist docs/build *.egg-info coverage.xml

dist:
	python setup.py sdist
	python setup.py bdist_wheel

docs: check-tox
	$(TOX) -e docs

docswatch: check-tox
	$(TOX) -e docs -- html livehtml

lint: check-tox
	$(TOX) -e lint

test: check-tox
	$(TOX)

.PHONY: help clean dist docs docswatch lint test
