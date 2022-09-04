PYTHON := python3
.PHONY: clean fix check

clean:
	$(PYTHON) -Bc "import pathlib; [p.unlink() for p in pathlib.Path('.').rglob('*.py[co]')]"
	$(PYTHON) -Bc "import pathlib; [p.rmdir() for p in pathlib.Path('.').rglob('__pycache__')]"
	rm -rf __pycache__ build *.egg-info .mypy_cache dist
	cd docs && make clean


# FIXES

fix-isort:
	$(PYTHON) -m isort . --settings-path pyproject.toml

fix-black:
	$(PYTHON) -m black . --config pyproject.toml

generate-schemas:
	$(PYTHON) main.py generate-schema

fix: fix-isort fix-black generate-schemas


# CHECKS

check-isort:
	$(PYTHON) -m isort . --settings-path pyproject.toml --check-only

check-black:
	$(PYTHON) -m black . --config pyproject.toml --check

check-mypy: 
	$(PYTHON) -m mypy . --config-file pyproject.toml

test:
	$(PYTHON) -m unittest -v $$(find . -name "*_test.py")

check: check-isort check-black check-mypy test


# BUILDS

build-pip:
	$(PYTHON) -m pip install . --upgrade

build-docs-html:
	cd docs && make html

build-docs-pdf:
	cd docs && make latexpdf
