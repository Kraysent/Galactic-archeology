PYTHON := python3

check-isort:
	isort --check-only --profile black .

check-flake8:
	flake8 --max-line-length=100 --ignore=E203 --per-file-ignores="__init__.py:F401" .

check-mypy:
	mypy --ignore-missing-imports .

check-style: check-isort check-flake8 check-mypy


fix-isort:
	isort --profile black .

fix-black:
	black --line-length 100 .

fix-style: fix-isort fix-black


update-schemas:
	$(PYTHON) main.py generate-schemas


build-pip:
	$(PYTHON) -m pip install . --upgrade

build-docs-html:
	cd docs && make html

build-docs-pdf:
	cd docs && make latexpdf

run-tests:
	$(PYTHON) -m unittest -v tests.tasks


clean:
	rm -rf __pycache__ build *.egg-info .mypy_cache
	cd docs && make clean