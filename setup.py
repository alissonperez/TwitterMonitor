from setuptools import setup
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
    url="https://github.com/alissonperez/TwitterMonitor",
    packages=packages,
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7",
        "Development Status :: 2 - Pre-Alpha",
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
    description="Small library to create monitoring routines with Twitter DM",
    long_description=("A small open source library to create monitoring "
                      "routines of any nature using direct messages (DM) of "
                      "Twitter. For each message send request, the library "
                      "will take all the followers of configured account "
                      "and send instantly a DM to each one.")
)
