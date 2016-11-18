[![Build Status](https://travis-ci.org/o2r-project/o2r-meta.svg?branch=master)](https://travis-ci.org/o2r-project/o2r-meta)

# o2r meta

This is a collection of metadata related micro services for the o2r-platform:

1. schema & documentation of the o2r metadata
2. metaextract - collect meta information from files or session
3. metaharvest - collect metadata from external sources via OAI-PMH
4. metavalidate - check if metadata set is valid to the schema
5. metabroker - translate metadat from o2r to third party schemas


## License

o2r-meta is licensed under Apache License, Version 2.0, see file LICENSE.
The documentation of the schemas available at ```o2r-meta/schema/docs/``` is licensed under a [CC-BY 4.0 International](https://creativecommons.org/licenses/by/4.0/) license.
Copyright (C) 2016 - o2r project.


## Installation

    pip install -r requirements.txt

or use dockerfiles where applicable.

---

## 1. schema & documentation

+ o2r metadata schema with example and documentation. Currently the main schema is an adaption of the codemeta schema for software metadata. In addition to that we provide a schema for UI metadata
+ Our schemas are designed as json schemas. XML versions are generated automatically but regarded as secondary.


---


## 2. metaextract

metaextract.py is a basic try to automate metadata extraction from Rmd and R scripts. It outputs raw metadata that are not yet o2r schema compliant but can be refined using the metabroker with o2r mapping on the outputs.

Required packages: ```PyYAML```, ```dicttoxml```, ```guess_language-spirit```

Usage:

    python metaextract.py -i INPUT_DIR [-o OUTPUT_DIR -s] [-xml]


+ the parameters ```-o``` and ```-s``` are mutual exclusive choice, one of them is required.
+ use ```-s``` to print outputs to screen. use ```-o``` together with a valid relative path to write output files. 
+ default output format is _json_. use -xml to change it to _xml_.


Example:

    python metaextract.py -i"tests" -o"tests"


+ use ```docker build``` command with the ```extract``` directory of this repository as the build context to build the Docker image.

Example:

    docker build -t o2r-meta extract
    docker run --rm -v $(pwd)/extract/tests:/meta o2r-meta -i /meta -o /meta/extracts

---

## 3. metaharvest

metaharvest.py collects OAI-PMH metadata from aggregation services like DataCite and parses them to assist the completion of a metadata set in o2r.

Required package: ```lxml```

Usage:

    python metaharvest.py -i INPUT_TYPE -q QUERY_STRING


Example:

    python metaharvest.py -i"doi" -q"10.14457/CU.THE.1989.1"

---


## 4. metavalidate

metavalidate.py is a simple validator for json schemas

Required package: ```jsonschema```

Usage:

    python metavalidate.py -s SCHEMA_PATH -c CANDIDATE_PATH

+ use relative paths.

Example:

    python metavalidate.py -s"../schema/json/o2r-meta-schema.json" -c"../schema/json/example1-valid.json"

+ use ```docker build``` command with the ```validate``` directory of this repository as the build context to build the Docker image.

Example:

    docker build -t o2r-meta validate
    docker run --rm -v $(pwd)/validate/tests:/meta o2r-meta -s ../schema/json/o2r-meta-schema.json -c ../schema/json/example1-valid.json

---

## 5. metabroker

metabroker.py is a translator for raw metadata from the o2r project and common metadata schemas such as DataCite etc.
Translation instructions are read from mapping files (json).


Required package: %

Usage:

    python metabroker.py -i INPUT_DIR -o OUTPUT_DIR

+ the script parses all json files in the input directory that begin with "meta_" (possible outputs of metaextract.py)

Example:

    python metabroker.py -i"tests" -o"tests"


