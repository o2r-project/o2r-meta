[![Build Status](https://travis-ci.org/o2r-project/o2r-meta.svg?branch=master)](https://travis-ci.org/o2r-project/o2r-meta)

# o2r meta

This is a collection of metadata related micro services for the o2r-platform, including our schema and documentation.

# installation

    pip install -r requirements.txt

## metaextract

metaextract.py is a basic try to automate metadata extraction from Rmd and R scripts.

Required packages: ```PyYAML```, ```dicttoxml```, ```guess_language-spirit```

Usage:

    python metaextract.py -i INPUT_DIR -o OUTPUT_DIR -m MODUS [-s]


+ use ```xml``` or ```json``` as ```MODUS```.
+ use optional ```-s``` to output to screen.

Example:

    python metaextract.py -i"tests" -o"tests" -m"json" [-s]


+ use ```docker build``` command with the ```extract``` directory of this repository as the build context to build the Docker image.

Example:

    docker build -t o2r-meta extract
    docker run --rm -v $(pwd)/extract/tests:/meta o2r-meta -i /meta -o /meta/extracts -m json

---

## metaharvester

metaharvest.py collects OAI-PMH metadata from Datacite and parses them to assist the completion of a metadata set in o2r.

Usage:

    python metaharvest.py -t QUERYTYPE -q QUERYTEXT

Example:

    python metaharvest.py -t"doi" -q"10.14457/CU.THE.1989.1"

---

## metabroker

metabroker.py is a translator for raw metadata from the o2r project and common metadata schemas such as DataCite etc.
Translation instructions are read from mapping files (json).


Required package: ~~```dicttoxml```~~

Usage:

    python metabroker.py -i INPUT_DIR -o OUTPUT_DIR

+ the script parses all json files in the input directory that begin with "meta_" (possible outputs of metaextract.py)

Example:

    python metabroker.py -i"tests" -o"tests"

---

## schema

+ o2r metadata schema with example and documentation. Currently the main schema is an adaption of the codemeta schema for software metadata. In addition to that we provide a schema for UI metadata
+ Our schemas are designed as json schemas. XML versions are generated automatically but regarded as secondary.

---

## metavalidate

metavalidate.py is a simple validator for json schemas

Required package: ```python_jsonschema_objects```

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

## License

o2r-meta is licensed under Apache License, Version 2.0, see file LICENSE.
The documentation of the schemas available at ```o2r-meta/schema/docs/``` is licensed under a [CC-BY 4.0 International](https://creativecommons.org/licenses/by/4.0/) license.
Copyright (C) 2016 - o2r project.