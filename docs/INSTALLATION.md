# Installation

These instructions will allow you to install the package and accompanying databases on Linux. Mac OS X computers operate similarly.
For any other systems, or if you cannot install the databases, we recommend installing via [docker](DOCKER.md).

## Pre-requisites
Installation requires [VariantValidator](https://github.com/openvar/variantValidator) and [VariantFormatter](https://github.com/openvar/variantFormatter)

## Download the source code

To download the source code simply clone the master branch.

```
$ git clone https://github.com/openvar/rest_variantValidator
$ cd rest_variantValidator
```

## Python 3.6 environment

When installing  we recommend using a virtual environment, as it requires specific versions of several libraries including python and sqlite. See the [VariantValidator](https://github.com/openvar/variantValidator) installation documentation

## Installing rest_variantValidator

To install rest_ariantValidator within your virtual environment run:
```
$ python setup.py install
```
