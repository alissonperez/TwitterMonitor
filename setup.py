from setuptools import setup
from twitter_monitor.common import version, Tc
import os
import sys

# Compile a list of packages available
packages = []
for dirpath, dirnames, filenames in os.walk("twitter_monitor"):
    if "__pycache__" in dirpath:
        continue

    packages.append(dirpath.replace("/", "."))

packages = set(packages)

long_description = ""
try:
    with file("docs/about.rst") as f:
        long_description = f.read()
except Exception as e:
    pass

if sys.version_info < (3,):
    print(Tc("ERROR: Python 2.x requires TwitterMonitor '0.x' version.").underline)
    print(Tc("If you are using pip, try:").fail)
    print("")
    print(Tc("sudo pip install 'twittermonitor<1'").warning)
    raise SystemExit(1)
else:
    setup(
        name="TwitterMonitor",
        version=version,
        author="Alisson R. Perez",
        author_email="alissonperez@gmail.com",
        url="https://github.com/alissonperez/TwitterMonitor",
        packages=packages,
        classifiers=[
            "Programming Language :: Python",
            "Programming Language :: Python :: 3.3",
            "Development Status :: 3 - Alpha",
            "Operating System :: MacOS",
            "Operating System :: Unix",
            "Environment :: Console",
            "Intended Audience :: Developers",
            "Intended Audience :: System Administrators",
            "Intended Audience :: Information Technology",
            "Topic :: Software Development :: Libraries",
            "Topic :: System :: Monitoring",
            "Topic :: Utilities",
        ],
        install_requires=[
            "tweepy>=2.3",
        ],
        description="Small library to create monitoring routines with "
        "Twitter DM. (Python >= 3.3)",
        long_description=long_description
    )
