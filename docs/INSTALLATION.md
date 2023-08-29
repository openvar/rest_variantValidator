# Installation

These instructions will allow you to install the package and accompanying databases on Linux. Mac OS X computers operate similarly.
For any other systems, or if you cannot install the databases, we recommend installing via [docker](DOCKER.md).

## Pre-requisites
Installation requires [VariantValidator](https://github.com/openvar/variantValidator) and [VariantFormatter](https://github.com/openvar/variantFormatter)

## Installing

Download the git repo
```bash
$ git clone https://github.com/openvar/rest_variantValidator
$ cd rest_variantValidator
```

Create a virtual environment - recommended
```bash
$ conda env create -f environment.yml
$ conda activate vvrest
```

See the [VariantValidator](https://github.com/openvar/variantValidator) installation documentation to install the
databases and set up configurations. You will need to run the confuguration script if you have not installed this API
previously. Contact admin if you are having any difficulties
