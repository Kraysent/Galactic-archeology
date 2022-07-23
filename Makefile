PYTHON := python3

check-isort:
	$(PYTHON) -m isort --check-only --profile black .

check-flake8:
	$(PYTHON) -m flake8 --max-line-length=100 --ignore=E203 --per-file-ignores="__init__.py:F401" .

check-mypy:
	$(PYTHON) -m mypy --python-version 3.10 --ignore-missing-imports .

test:
	$(PYTHON) -m unittest -v tests.tasks

check: check-isort check-flake8 check-mypy test


fix-isort:
	isort --profile black .

fix-black:
	black --line-length 100 .

generate-schemas:
	$(PYTHON) main.py generate-schema

fix: fix-isort fix-black generate-schemas


update-schemas:
	$(PYTHON) main.py generate-schemas


build-pip:
	$(PYTHON) -m pip install . --upgrade

build-docs-html:
	cd docs && make html

build-docs-pdf:
	cd docs && make latexpdf


clean:
	rm -rf __pycache__ build *.egg-info .mypy_cache
	cd docs && make clean