#!/usr/bin/env python

# Prefer setuptools over distutils
from setuptools import setup

setup(
    name='rest_VariantValidator',
    use_scm_version=True,
    zip_safe=True,
    author="VariantValidator Contributors",
    author_email = 'admin@variantvalidator.org',
    description='Rest API for VariantValidator',
    long_description=open('README.md').read(),
    url='https://github.com/openvar/variantFormatter',
    license="GNU AFFERO GENERAL PUBLIC LICENSE, Version 3 (https://www.gnu.org/licenses/agpl-3.0.en.html)",
    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 3 - Alpha',

        # Audience
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',

        # Specify the Python versions
        'Programming Language :: Python',
    ],

    # What does your project relate to?
    keywords=[
        "bioinformatics",
        "computational biology",
        "genome variants",
        "genome variation",
        "genomic variants",
        "genomic variation",
        "genomics",
        "hgvs",
        "HGVS",
        "sequencevariants",
    ],

    setup_requires=[
        "setuptools_scm",
    ]
)

# <LICENSE>
# Copyright (C) 2016-2022 VariantValidator Contributors
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
# </LICENSE>
