#!/usr/bin/bash
# Run this bash script to publish the package to PyPi
test=True

python encoder.py
python3 setup.py sdist bdist_wheel
if $test; then
  python3 -m twine upload --repository testpypi dist/*
else
  python3 -m twine upload dist/*
fi
