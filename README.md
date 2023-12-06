# rest_VariantValidator
[![Build Status](http://127.0.0.1:8080/job/rest_VariantValidator%20CI/job/master/badge/icon)](http://127.0.0.1:8080/job/rest_VariantValidator%20CI/job/master/)
[![codecov](https://codecov.io/gh/openvar/rest_variantValidator/graph/badge.svg?token=DE92ZVZT3F)](https://codecov.io/gh/openvar/rest_variantValidator)

## About rest_variantValidator

rest_variantValidator is a rest web interface for VariantValidator

## About VariantValidator

VariantValidator is a user-friendly software tool designed to validate the syntax and 
parameters of DNA variant descriptions according to the HGVS Sequence Variant 
Nomenclature. 

VariantValidator ensures that users are guided through the intricacies of the HGVS 
nomenclature, e.g. if the user makes a mistake, VariantValidator automatically corrects 
the mistake if it can, or provides helpful guidance if it cannot. In addition, 
VariantValidator accurately interconverts between transcript variant descriptions and 
genomic variant descriptions in HGVS and Variant Call Format (VCF)

VariantValidator interfaces with the hgvs package to parse, format, and manipulate 
biological sequence variants.  See https://github.com/biocommons/hgvs/ for details of the
hgvs package

VariantValidator is a highly functional platform enabling high-throughput and embeddable
utilisation of functionality of https://variantvalidator.org/

## Features

The basic functionality of https://variantvalidator.org/ and VarinantValidator is documented here https://www.ncbi.nlm.nih.gov/pubmed/28967166

VariantValidator simultaneously and accurately projects genomic sequence variations onto all overlapping transcript reference sequences, and vice-versa

Alternatively, genomic sequence variation can be projected onto a specified single, or specified subset of transcript reference sequences for any given gene

Projection of sequence variations between reference sequences takes account of discrepancies between genomic and transcript reference sequences, thus ensuring an accurate prediction of the effect on encoded proteins for every gene

For sequence variations falling within the open reading frames of genes, VariantValidator automatically projects sequence variants via the transcript reference sequence onto genome builds GRCh38, GRCh37, hg38 and hg19 (HGVS format and VCF components), including projection onto relevant Alternative genomic reference sequences, the composition of which varies between patched GRC genome builds and static hg genome builds

## Pre-requisites

VariantValidator will work on Mac OS X or Linux operating systems.

Required software:
* MySQL
* Python 2.7
* SQLite version 3.8.0 or above

Optional software:
* Postgres version 9.5 or above

For installation instructions please see [INSTALLATION.md](./docs/INSTALLATION.md)

## Operation and configuration

Please see [MANUAL.md](./docs/MANUAL.md)

# Running in docker

Please see [DOCKER.md](https://github.com/openvar/rest_variantValidator/blob/master/docs/DOCKER.md)

## License

Please see [LICENSE.txt](LICENSE.txt)

## Terms and conditions of use
[Terms and conditions can be found here](https://github.com/openvar/variantValidator/blob/master/README.md)

## Cite us

Hum Mutat. 2017 Oct 1. doi: 10.1002/humu.23348

VariantValidator: Accurate validation, mapping and formatting of sequence variation descriptions.

Freeman PJ, Hart RK, Gretton LJ, Brookes AJ, Dalgleish R.

> Copyright (C) 2018  Peter Causey-Freeman, University of Leicester
> 
> This program is free software: you can redistribute it and/or modify
> it under the terms of the GNU Affero General Public License as
> published by the Free Software Foundation, either version 3 of the
> License, or (at your option) any later version.
> 
> This program is distributed in the hope that it will be useful,
> but WITHOUT ANY WARRANTY; without even the implied warranty of
> MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
> GNU Affero General Public License for more details.
> 
> You should have received a copy of the GNU Affero General Public License
> along with this program.  If not, see <https://www.gnu.org/licenses/>.
> </LICENSE>

