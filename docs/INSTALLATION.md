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



When installing  we have found that some of the VariantValidator dependencies do not load well using pip.
Instead, install using anaconda and the pre-configured environment.yml

```bash
$ conda env create -f environment.yml
$ conda activate vvrest
$ pip install -r REQUIREMENTS.txt
```
 
Only if you have never installed VariantValidator perform the following command otherwise your previous config will be
over-written

```bash
cp ./configuration ~/.variantvalidator
```

See the [VariantValidator](https://github.com/openvar/variantValidator) installation documentation to install the
databases and set up configurations. Contact admin if you are having any difficulties
