import setuptools

import insomniac

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="insomniac",
    version=insomniac.__version__,
    author="Alexander Mishchenko",
    author_email="5740235@gmail.com",
    description="Insomniac: Instagram bot for automated Instagram interaction using Android device via ADB",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/alexal1/Insomniac",
    packages=setuptools.find_packages(),
    install_requires=['colorama', 'uiautomator', 'uiautomator2'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    include_package_data=True
)
