[![Build Status](https://travis-ci.org/o2r-project/o2r-meta.svg?branch=master)](https://travis-ci.org/o2r-project/o2r-meta)

# o2r meta

This is a collection of metadata related micro services for the o2r-platform:

1. schema & documentation of the o2r metadata
2. extract - collect meta information from files or session
3. broker - translate metadata from o2r to third party schemas
4. validate - check if metadata set is valid to the schema
5. harvest - collect metadata from external sources via OAI-PMH
 

For their role within o2r, please see [o2r-architecture](https://github.com/o2r-project/architecture).

## License

o2r-meta is licensed under Apache License, Version 2.0, see file LICENSE.
The documentation of the schemas available at ```o2r-meta/schema/docs/``` is licensed under a [CC-BY 4.0 International](https://creativecommons.org/licenses/by/4.0/) license.
Copyright (C) 2016,2017 - o2r project.


## Installation
(1) Acquire Python version 3.6.
(2) Install the required modules:

    pip install -r requirements.txt

	
## Usage

Chosing the right tool:

    python o2rmeta [-debug] extract|validate|broker|harvest <ARGS>

Explanation of the main switches:
+ `debug` : option to enable verbose debug info where applicable	

Providing arguments for each tool:

#(1) Extractor tool:

	python o2rmeta extract -i <INPUT_DIR> -s|-o <OUTPUT_DIR> [-xo] [-m] [-xml] [-ercid <ERC_ID>]
	
Example call:
	
	python o2rmeta extract -i new/tests -o myOutputDir -xo -m
	
Explanation of the switches:

+ `-i` <INPUT_DIR> : required starting path for recursive search for parsable files
+ `-s`: option to print out results to console. This switch is mutually exclusive with `-o`. At least one of them must be given
+ `-o` <OUTPUT_DIR> : required output path, where data should be saved. This switch is mutually exclusive with `-s`. At least one of them must be given.
+ `-xo` : option to disable orcid public API calls
+ `-m` : option to additionally enable output of all processed files
+ `-xml` : option to change output format from json (default) to xml
+ `-ercid` <ERC_ID>: option to provide an ERC identifier


#(2) broker
TBD

#(3) validate
TBD

#(4) harvest
TBD
