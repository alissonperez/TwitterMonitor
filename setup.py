from distutils.core import setup
from twitter_monitor.common import version
import os

# Compile a list of packages available
packages = []
for dirpath, dirnames, filenames in os.walk("twitter_monitor"):
    if "__pycache__" in dirpath:
        continue

    packages.append(dirpath.replace("/", "."))

packages = set(packages)

setup(
    name="TwitterMonitor",
    version=version,
    author="Alisson R. Perez",
    author_email="alissonperez@gmail.com",
    # @todo - Update with our PyPI package page
    url="https://pypi.python.org/pypi",
    packages=packages,
    # scripts=["bin/loremdb"],
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7",
        "Development Status :: 1 - Planning",
        "Operating System :: OS Independent",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "Topic :: Database",
    ],
    install_requires=[
        "tweepy>=2.3",
    ],
    # @todo - Include: "description" and "long_description"
)
