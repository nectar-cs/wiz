#!/bin/bash

rm -rf build
rm -rf dist


pipenv lock -r > requirements.txt
pip3 install -r requirements.txt

pipenv run python3 setup.py sdist bdist_wheel
pipenv run twine upload -u xnectar -p "$PYPI_PASSWORD" dist/*

rm -rf build
rm -rf dist