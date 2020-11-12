#!/usr/bin/bash
# Run this bash script to publish the package to PyPi
test=True
version=$(sed -n "s/.*__version__ = .\([0-9.]*\).*/\1/p" ./insomniac/__version__.py)
echo "Publishing: test=$test, version=$version"

python3 stubs_generator.py
git tag v"$version"
git push --tags
python3 setup.py sdist bdist_wheel
if $test; then
  python3 -m twine upload --repository testpypi dist/*
else
  python3 -m twine upload dist/*
fi
