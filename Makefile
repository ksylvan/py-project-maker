# Convenience Makefile for pyhatchery
#
# This Makefile is used to automate common tasks for the pyhatchery project.
# It provides a simple interface for running tests, and generating coverage reports.

.PHONY: help bootstrap test coverage coverage-html format

COVERAGE_FAIL_UNDER := 80
COVERAGE_SRC := src/pyhatchery

help:
	@echo "Usage: make [help | bootstrap | test | coverage | coverage-html | format | linters]"
	@echo ""
	@echo "Available targets:"
	@echo "  bootstrap      : Set up the development environment."
	@echo "  test           : Run tests."
	@echo "  coverage       : Run tests and generate a coverage report."
	@echo "  coverage-html  : Run tests and generate an HTML coverage report."
	@echo "  format         : Format the code using ruff."
	@echo "  linters        : Run linters (ruff and pylint)."

bootstrap:
	# This will remove and re-create the virtual environment,
	# installing all dependencies.
	./bootstrap/setup.sh -F

test:
	uv run pytest -v

coverage:
	uv run pytest -v --cov=$(COVERAGE_SRC) \
		-ra -q \
		--cov-report=term-missing \
		--cov-fail-under=$(COVERAGE_FAIL_UNDER)

coverage-html:
	# This will generate an HTML coverage report.
	uv run pytest --cov=$(COVERAGE_SRC) \
		--cov-report=html:coverage_html \
		--cov-fail-under=$(COVERAGE_FAIL_UNDER)

format:
	uv run ruff format .

linters:
	uv run ruff check .
	uv run pylint .
