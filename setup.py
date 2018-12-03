#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""
import os
import re
from setuptools import setup, find_packages

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

with open(os.path.join('ndex_webapp_python_exporters','__init__.py')) as ver_file:
    for line in ver_file:
        if line.startswith('__version__'):
            version=re.sub("'","",line[line.index("'"):])
 
requirements = [ 
    "argparse",
    "ndex2"
]

setup_requirements = [ ]

test_requirements = [ 
    "argparse",
    "ndex2",
    "networkx==1.11",
    "unittest2"
]

setup(
    author="Chris Churas",
    author_email='churas.camera@gmail.com',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
    scripts=['ndex_webapp_python_exporters/ndex_exporters.py'],
    description="Command line exporters written in Python used by the NDex REST service",
    install_requires=requirements,
    license="BSD license",
    long_description=readme + '\n\n' + history,
    include_package_data=True,
    keywords='ndex_webapp_python_exporters',
    name='ndex_webapp_python_exporters',
    packages=find_packages(include=['ndex_webapp_python_exporters']),
    setup_requires=setup_requirements,
    test_suite='tests',
    tests_require=test_requirements,
    url='https://github.com/ndexbio/ndex_webapp_python_exporters',
    version=version,
    zip_safe=False,
)
