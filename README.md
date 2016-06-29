[![Build Status](https://travis-ci.org/o2r-project/o2r-meta.svg?branch=master)](https://travis-ci.org/o2r-project/o2r-meta)

#o2r metadata sets

###metaextract

metaextract.py is a very basic try to automate metadata extraction from R scripts, including comments. inputs should be R scripts (.R) and Rmarkdown (.rmd) in a dir called 'tests'. outputs are xml files.

Usage:

    python metaextract.py -i INPUT_DIR -o OUTPUT_FORMAT

use ```xml``` or ```json``` as OUTPUT_FORMAT

Example:

    python metaextract.py -i"tests" -o"json"

---

###schema

+ currently codemeta json schema adaption

---

###validator
validate.py is simple validator for json schemas

Required package: ```json-schema```

Usage:

    python validate.py -s SCHEMA_PATH -c CANDIDATE_PATH

Example:

    python validate.py -s"../schema/json/o2r-meta-schema.json" -c"../schema/json/example1-valid.json"