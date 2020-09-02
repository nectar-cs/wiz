#!/bin/bash

rm -rf build
rm -rf dist

python3 setup.py sdist bdist_wheel
twine upload -u xnectar -p "$PYPI_PASSWORD" dist/*

rm -rf build
rm -rf dist