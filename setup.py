#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2025, Eldes, Matteo Galletti <m.galletti@eldes.it>

import glob
from setuptools import setup, find_packages

requirements = [
    'numpy',
]

setup_requirements = [
#    'setuptools_scm',
]

test_requirements = [
]

extras = {
}

packages = find_packages(include=['pymetranet'])

package_dir = {}

package_data = {}

scripts = glob.glob('examples/*.py') 

setup(
    name='pymetranet',
    #use_scm_version=True,
    version="0.3.0",
    author="Eldes",
    author_email='info@eldes.t',
    description='Python Metranet library',
    url='https://www.eldesradar.com',
    classifiers=[
        'License :: OSI Approved :: BSD-3-Clause License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3.7-3.8-3.9',
    ],
    keywords='pymetranet',
    entry_points={},
    scripts=scripts,
    license="BSD-3-Clause license",
    long_description=open('README.md').read(),
    include_package_data=True,
    zip_safe=False,
    test_suite='test',
    py_modules=['pymetranet'],
    packages=packages,
    install_requires=requirements,
    package_dir=package_dir,
    package_data=package_data,
    setup_requires=setup_requirements,
    tests_require=test_requirements,
    extras_require=extras
)
