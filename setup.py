#!/usr/bin/env python3
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

extras = {
}

packages = find_packages(include=['pymetranet'])

package_dir = {}

package_data = {'pymetranet': ['libpymetranet.so']}

scripts = glob.glob('examples/*.py') 

setup(
    name='pymetranet',
    #use_scm_version=True,
    version="0.3.0",
    author="Eldes",
    author_email='info@eldes.t',
    description='Python Metranet library',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/eldesradar/pymetranet',
    license="BSD-3-Clause license",
    license_expression="BSD-3-Clause",
    classifiers=[
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9'
    ],
    keywords='pymetranet',
    entry_points={},
    scripts=scripts,
    zip_safe=False,
    py_modules=['pymetranet'],
    packages=packages,
    python_requires='>=3.6',
    install_requires=requirements,
    package_dir=package_dir,
    package_data=package_data,
    include_package_data=True,
    setup_requires=setup_requirements,
    extras_require=extras
)
