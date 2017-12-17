src_dir := igd

python ?= python3.6
VIRTUAL_ENV ?= pyenv
pip := $(VIRTUAL_ENV)/bin/python -m pip
pytest := $(VIRTUAL_ENV)/bin/py.test
linter := $(VIRTUAL_ENV)/bin/python -m flake8
py_requirements ?= requirements/prod.txt requirements/dev.txt
mypy := $(VIRTUAL_ENV)/bin/python -m mypy


.PHONY: test
test: $(VIRTUAL_ENV)
	PYTHONPATH=$(PYTHONPATH):. $(pytest) -s --cov=$(src_dir) tests

.PHONY: lint
lint: $(VIRTUAL_ENV)
	$(linter) $(src_dir)

.PHONY: check-types
check-types: $(VIRTUAL_ENV)
	$(mypy) --ignore-missing-imports $(src_dir)

.PHONY: security-test
security-test: $(virtualenv_dir)
	$(VIRTUAL_ENV)/bin/bandit -r $(src_dir)

$(VIRTUAL_ENV): $(py_requirements)
	$(python) -m venv $@
	for r in $^ ; do \
		$(pip) install -r $$r ; \
	done
