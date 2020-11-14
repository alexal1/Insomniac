import setuptools

from insomniac.__version__ import __version__

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="insomniac",
    version=__version__,
    author="Insomniac Team",
    author_email="info@insomniac-bot.com",
    description="Insomniac: Instagram bot for automated Instagram interaction using Android device via ADB",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/alexal1/Insomniac",
    packages=setuptools.find_packages(),
    install_requires=['colorama', 'uiautomator', 'uiautomator2', 'croniter'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    include_package_data=True
)
