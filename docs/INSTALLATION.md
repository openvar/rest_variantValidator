# Installation

These instructions will allow you to install the package and accompanying databases on Linux. Mac OS X computers operate similarly.
For any other systems, or if you cannot install the databases, we recommend installing via [docker](DOCKER.md).

## Pre-requisites
Installation requires [VariantValidator](https://github.com/openvar/variantValidator) and [VariantFormatter](https://github.com/openvar/variantFormatter)

## Installing VariantValidator

When installing  we have found that some of the VariantValidator dependencies do not load well using pip.
Instead install VariantValidator first using anaconda and the pre-configured environment.yml 
See the [VariantValidator](https://github.com/openvar/variantValidator) installation documentation

## Download the source code

To download the source code simply clone the master branch.

```
$ git clone https://github.com/openvar/rest_variantValidator
$ cd rest_variantValidator
```

## Installing rest_variantValidator

To install rest_variantValidator within your virtual environment, activate the environment and run:
```
$ pip install -e .
```
