import setuptools

from insomniac.__version__ import __version__

with open("README.md", "r", errors='ignore') as fh:
    long_description = fh.read()

with open("requirements.txt", "r") as file:
    install_requires = [line.rstrip() for line in file]

setuptools.setup(
    name="insomniac",
    version=__version__,
    author="Insomniac Team",
    author_email="info@insomniac-bot.com",
    description="Insomniac: Instagram bot for automated Instagram interaction using Android device via ADB",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/alexal1/Insomniac",
    packages=setuptools.find_packages(exclude=[
        'registration',
        'registration.*',
        'insomniac_webui_server',
        'insomniac_webui_server.*'
    ]),
    install_requires=install_requires,
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    include_package_data=True
)
