# -*- coding: utf-8 -*-

__version__ = '1.0.1'

import os
import re
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

with open(os.path.join(os.path.dirname(__file__), 'network_interfaces', '__init__.py')) as v_file:
    package_version = re.compile(r".*__version__ = '(.*?)'", re.S).match(v_file.read()).group(1)

dependencies = [
    'ipcalc'
]


def read(filename):
    return open(os.path.join(os.path.dirname(__file__), filename)).read()

setup(
    name="network_interfaces",
    version=package_version,
    author="Vahid Mardani",
    author_email="vahid.mardani@gmail.com",
    url="https://github.com/pylover/network-interfaces",
    description="Python Library to parse and manipulate the /etc/network/interfaces file",
    maintainer="Vahid Mardani",
    maintainer_email="vahid.mardani@gmail.com",
    packages=['network_interfaces'],
    package_data={'network_interfaces': ['tests/data/**/*']},
    platforms=["any"],
    long_description=read('README.md'),
    install_requires=dependencies,
    classifiers=[
        "License :: Freeware",
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Topic :: Software Development :: Libraries'
    ],
)
