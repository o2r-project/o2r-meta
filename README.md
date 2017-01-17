[![Build Status](https://travis-ci.org/o2r-project/o2r-meta.svg?branch=master)](https://travis-ci.org/o2r-project/o2r-meta)

# o2r meta

This is a collection of metadata related micro services for the o2r-platform:

1. schema & documentation of the o2r metadata
2. extract - collect meta information from files or session
3. broker - translate metadata from o2r to third party schemas
4. validate - check if metadata set is valid to the schema
5. harvest - collect metadata from external sources via OAI-PMH
 

For their role within o2r, please refer to [o2r-architecture](https://github.com/o2r-project/architecture).

## License

o2r-meta is licensed under Apache License, Version 2.0, see file LICENSE.
The documentation of the schemas available at ```o2r-meta/schema/docs/``` is licensed under a [CC-BY 4.0 International](https://creativecommons.org/licenses/by/4.0/) license.
Copyright (C) 2016, 2017 - o2r project.


## Installation
_Note:_ o2r meta is designed for python 3.6 but supports python 3.4+.

(1) Acquire Python version 3.4+.

(2) Parts of o2r meta require the _gdal_ module that is known for causing trouble when installed via _PIP_. Therefore it is recommended to prepare the installation like this:

    sudo add-apt-repository ppa:ubuntugis/ppa -y
    sudo add-apt-repository ppa:ubuntugis/ubuntugis-unstable -y
    sudo apt-get -qq update
    sudo apt-get install -y python3-dev
    sudo apt-get install -y libgdal-dev
    sudo apt-get build-dep -y python-gdal
    sudo apt-get install -y python-gdal
    export CPLUS_INCLUDE_PATH=/usr/include/gdal
    export C_INCLUDE_PATH=/usr/include/gdal

and afterwards install _gdal_ this way:

    pip install GDAL==$(gdal-config --version | awk -F'[.]' '{print $1"."$2}')

Alternatively you can use a precompiled python wheel of the gdal module that fits your desired platform.

(3) Install the required modules:

    pip install -r requirements.txt

	
## Usage

When calling o2r meta, you can chose from the following commands, each representing one tool of the o2r meta suite: _extract_, _validate_, _broker_ and _harvest_.

    python o2rmeta [-debug] extract|validate|broker|harvest <ARGS>

Explanation of the main switches:
+ `debug` : option to enable verbose debug info where applicable	

Each tool then has a number of required arguments:

#(1) Extractor tool:

	python o2rmeta extract -i <INPUT_DIR> -s|-o <OUTPUT_DIR> [-xo] [-m] [-xml] [-ercid <ERC_ID>]
	
Example call:
	
	python o2rmeta extract -i extract/tests -o extract/tests -xo
	
Explanation of the switches:

+ `-i` <INPUT_DIR> : required starting path for recursive search for parsable files
+ `-s`: option to print out results to console. This switch is mutually exclusive with `-o`. At least one of them must be given
+ `-o` <OUTPUT_DIR> : required output path, where data should be saved. If the directory does not exist, it will be created on runtime. This switch is mutually exclusive with `-s`. At least one of them must be given.
+ `-xo` : option to disable orcid public API calls
+ `-m` : option to additionally enable individual output of all processed files.
+ `-xml` : option to change output format from json (default) to xml.
+ `-ercid` <ERC_ID>: option to provide an ERC identifier.


#(2) broker
TDB

#(3) Validator tool:

	python o2rmeta validate -s <SCHEMA> -c <CANDIDATE>
	
Example call:
	
	python o2rmeta validate -s schema/json/o2r-meta-schema.json -c schema/json/example1-valid.json

Explanation of the switches:

+ `-s` <SCHEMA> : required path or URL to the schema file, can be json or xml. 
+ `-c` <CANDIDATE> : required path to candidate that shall be validated

#(4) harvest
TBD
