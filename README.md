[![Build Status](https://travis-ci.org/o2r-project/o2r-meta.svg?branch=master)](https://travis-ci.org/o2r-project/o2r-meta)

#o2r metadata sets

###metaextract

metaextract.py is a very basic try to automate metadata extraction from Rmd and R scripts.

Required package: ```PyYAML```, ```dicttoxml```

Usage:

    python metaextract.py -i INPUT_DIR -o OUTPUT_FORMAT


+ use ```xml``` or ```json``` as ```OUTPUT_FORMAT```.

Example:

    python metaextract.py -i"tests" -o"json"

+ use ```docker build``` command on the ```extract``` directory of this repository to build the docker container.

Example:
 
    docker build --no-cache extract

---

###schema

+ o2r metadata schema. Currently an adaption of the codemeta json schema for software metadata.

---

###validate

validate.py is a simple validator for json schemas

Required package: ```json-schema```

Usage:

    python validate.py -s SCHEMA_PATH -c CANDIDATE_PATH

use relative paths.

Example:

    python validate.py -s"../schema/json/o2r-meta-schema.json" -c"../schema/json/example1-valid.json"