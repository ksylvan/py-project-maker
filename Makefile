# Convenience Makefile for pyhatchery
#
# This Makefile is used to automate common tasks for the pyhatchery project.
# It provides a simple interface for running tests, and generating coverage reports.

.PHONY: bootstrap test coverage coverage-html format

COVERAGE_FAIL_UNDER := 80
COVERAGE_SRC := src/pyhatchery

bootstrap:
	# This will remove and re-create the virtual environment,
	# installing all dependencies.
	./bootstrap/setup.sh -F

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

test:
	uv run pytest -v