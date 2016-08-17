[![Build Status](https://travis-ci.org/o2r-project/o2r-meta.svg?branch=master)](https://travis-ci.org/o2r-project/o2r-meta)

# o2r metadata sets

## metaextract

metaextract.py is a very basic try to automate metadata extraction from Rmd and R scripts.

Required package: ```PyYAML```, ```dicttoxml```

Usage:

    python metaextract.py -i INPUT_DIR -o OUTPUT_FORMAT -e OUTPUT_DIR [-s]


+ use ```xml``` or ```json``` as ```OUTPUT_FORMAT```.
+ use optional ```-s``` to output to screen.

Example:

    python metaextract.py -i"tests" -o"json" -e"tests" [-s]


+ use ```docker build``` command with the ```extract``` directory of this repository as the build context to build the Docker image.

Example:

    docker build -t o2r-meta extract
    docker run --rm -v $(pwd)/extract/tests:/meta o2r-meta -i /meta -o json -e /meta/extracts
    docker run --rm -v $(pwd)/extract/tests:/meta o2r-meta -i /meta -o xml -e /meta/extracts
    docker run --rm -v $(pwd)/extract/tests:/meta o2r-meta -i /meta -o json -e /meta/extracts -s

---

## schema

+ o2r metadata schema. Currently an adaption of the codemeta json schema for software metadata.

---

## metavalidate

metavalidate.py is a simple validator for json schemas

Required package: ```json-spec```

Usage:

    python metavalidate.py -s SCHEMA_PATH -c CANDIDATE_PATH

use relative paths.

Example:

    python metavalidate.py -s"../schema/json/o2r-meta-schema.json" -c"../schema/json/example1-valid.json"

---

## License

o2r-meta is licensed under Apache License, Version 2.0, see file LICENSE.

Copyright (C) 2016 - o2r project.