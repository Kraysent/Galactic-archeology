PYTHON := python3

check-isort:
	$(PYTHON) -m isort --check-only --profile black .

check-flake8:
	$(PYTHON) -m flake8 --max-line-length=100 --ignore=E203 --per-file-ignores="__init__.py:F401" .

check-omtool-mypy:
	$(PYTHON) -m mypy omtool --python-version 3.10 --ignore-missing-imports

check-cli-mypy:
	$(PYTHON) -m mypy cli --python-version 3.10 --ignore-missing-imports

check-tools-mypy:
	$(PYTHON) -m mypy tools --python-version 3.10 --ignore-missing-imports

check-tests-mypy:
	$(PYTHON) -m mypy tests --python-version 3.10 --ignore-missing-imports

check-mypy: check-omtool-mypy check-tools-mypy check-cli-mypy check-tests-mypy

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


build-pip:
	$(PYTHON) -m pip install . --upgrade

build-docs-html:
	cd docs && make html

build-docs-pdf:
	cd docs && make latexpdf


clean:
	$(PYTHON) -Bc "import pathlib; [p.unlink() for p in pathlib.Path('.').rglob('*.py[co]')]"
	$(PYTHON) -Bc "import pathlib; [p.rmdir() for p in pathlib.Path('.').rglob('__pycache__')]"
	rm -rf __pycache__ build *.egg-info .mypy_cache dist
	cd docs && make clean