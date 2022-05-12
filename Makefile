build-pip:
	python3 -m pip install . --upgrade

build-docs-html:
	cd docs && make html

build-docs-pdf:
	cd docs && make latexpdf

clean:
	rm -rf __pycache__ build *.egg-info .mypy_cache
	cd docs && make clean