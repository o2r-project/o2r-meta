**DEV** | **MASTER** 
------ | ------ |
[![Build Status](https://travis-ci.org/o2r-project/o2r-meta.svg?branch=dev)](https://travis-ci.org/o2r-project/o2r-meta) |[![Build Status](https://travis-ci.org/o2r-project/o2r-meta.svg?branch=master)](https://travis-ci.org/o2r-project/o2r-meta)
current development branch<br> containing latest updates | "stable" branch for<br> o2r ref. implementation |

# o2r meta

This is a collection of tools for extract-map-validate workflows. 

0. schema & documentation of the o2r metadata
1. extract - collect meta information from files in a workspace
2. broker - translate metadata from o2r to third party schemas
3. validate - check if metadata set is valid to the schema
4. harvest - collect metadata from external sources via OAI-PMH
5. adding new parsers to the program

For their role within o2r, please refer to [o2r-architecture](https://github.com/o2r-project/architecture).

## License

o2r-meta is licensed under Apache License, Version 2.0, see file LICENSE. Copyright (C) 2016, 2017 - o2r project.

## Installation

(1) Acquire python 3.6

(2) Install the required modules:

    pip install -r requirements.txt

### Using Docker

Another way of installation is provided by the Dockerfile. Build it like this:

    docker build -t meta .

And start a tool of o2r meta like this:

	docker run --rm -v $(pwd)/extract/tests/:/testdata:ro meta -debug extract -i /testdata -s

You can pass all options to the images as if running `o2rmeta.py` directly, but must naturally mount all required data into the container.

The container has a default user `o2r` (`UID: 1000`) to avoid permission issues when mounting directories, e.g.

	mkdir /tmp/testout
	docker run --rm -v $(pwd)/extract/tests/:/testdata:ro -v /tmp/testout:/testout:rw meta -debug extract -i /testdata -o /testout
	ls /tmp/testout

Note: if the directory does not exist before mounting it, then Docker will create it for the user root and permission errors will arise.

## Documentation

+ Current documentation as part of the [ERC-SPEC](https://o2r.info/erc-spec/spec/schema/) ([GitHub](https://github.com/o2r-project/erc-spec/blob/master/docs/spec/schema.md))
+ Current elements of raw and o2r MD: [elements.md](schema/docs/elements.md)
+ Current o2r [metadata schema](https://raw.githubusercontent.com/o2r-project/o2r-meta/master/schema/json/o2r-meta-schema.json)
+ [MD of the erc configuration file](https://o2r.info/erc-spec/spec/#erc-configuration-file)

## Usage

When calling o2r meta, you can chose from the following commands, each representing one tool of the o2r meta suite: _extract_, _validate_, _broker_ and _harvest_.

    python o2rmeta [-debug] extract|validate|broker|harvest <ARGS>

Options:

+ `-debug` : option to enable raise error and provide verbose debug info where applicable	

Each tool then has a number of arguments:

# (1) Extractor tool:

	python o2rmeta.py extract -i <INPUT_DIR> -s|-o <OUTPUT_DIR> [-xo] [-m] [-xml] [-ercid <ERC_ID>]
	
Example call:
	
	python o2rmeta.py -debug extract -i extract/tests -o extract/tests -xo
	
Explanation of the switches:

+ `-f` returns a list of supported file formats (extensions) and terminates program
+ `-i` <INPUT_DIR> : starting path for recursive search for parsable files
+ `-s`: option to print out results to console. This switch is mutually exclusive with `-o`. At least one of them must be given
+ `-o` <OUTPUT_DIR> : output path, where data should be saved. If the directory does not exist, it will be created on runtime. This switch is mutually exclusive with `-s`. At least one of them must be given.
+ `-xo` : option to disable http requests (the extractor will stay offline. This disables orcid retrieval, erc spec download, doi retrieval, ...)
+ `-m` : option to additionally enable individual output of all processed files.
+ `-xml` : option to change output format from json (default) to xml.
+ `-ercid` <ERC_ID>: option to provide an ERC identifier.
+ `-b` <BASE_DIR>: option to provide starting point directory for relative paths output

### Supported files and formats for the metadata extraction process:

Use `python o2rmeta.py extract -f` to see supported formats.

# (2) Broker: A mapping tool

The broker has two modes: In _mapping mode_, it creates fitting metadata for a given map by following a translation scheme included in that mapping file.
In _checking mode_ it returns missing metadata information for a target service or plattform, e.g. zenodo publication metadata, for a given checklist and input data.

The broker can be used to translate between different standards for metadata sets. A typical workflow would look as follows:
Step 1: Convert extracted raw metadata to o2r schema compliant metadata.
Step 2: Convert o2r metadata to a 3rd party repository schema, e.g. zenodo.

Each Step can be done with a single call of the broker.
 
Translation instructions as well as checklists are stored in json formatted map files, documented at [schema/docs/mappings_docs.md](https://github.com/o2r-project/o2r-meta/tree/master/schema/docs/mappings_docs.md).

    python o2rmeta.py broker -i <INPUT_FILE> -c <CHECKLIST_FILE>|-m <MAPPING_FILE> -s|-o <OUTPUT_DIR>
	
Example calls:
	
    python o2rmeta.py -debug broker -c broker/checks/zenodo-check.json -i schema/json/example_zenodo.json -o broker/tests/all

    python o2rmeta.py -debug broker -m broker/mappings/zenodo-map.json -i broker/tests/metadata_o2r.json -o broker/tests/all

Explanation of the switches:

+ `-c` <CHECKLIST_FILE> : required path to a json checklist file that holds checking instructions for the metadata. This switch is mutually exclusive with `-m`. At least one of them must be given.
+ `-m` <MAPPING_FILE> : required path to a json mapping file that holds translation instructions for the metadata mappings. This switch is mutually exclusive with `-c`. At least one of them must be given.
+ `-i` <INPUT_FILE> : path to input json file.
+ `-s`: option to print out results to console. This switch is mutually exclusive with `-o`. At least one of them must be given.
+ `-o` <OUTPUT_DIR> : required output path, where data should be saved. If the directory does not exist, it will be created on runtime. This switch is mutually exclusive with `-s`. At least one of them must be given.

Supported checks/maps

**service** | **checklist file** | **mapping file** | **status** | **comment**
------ | ------ | ------ | ------ | ------ |
zenodo| zenodo-check.json | zenodo-map.json | _WIP_ | _zenodo will register MD @ datacite.org_
eudat b2share| eudat-b2share-check.json | eudat-b2share-map.json | _WIP_ | b2share supports custom MD schemas
... | ... | ... | ... | ...

Additionally the following features will be made available in the future:
+ Documentation of the formal map-file "minimal language" (create your own map-files).
+ Governing JSON-Schema for the map files (validate map-files against the map-file-schema).

# (3) Validator tool:

	python o2rmeta.py validate -s <SCHEMA> -c <CANDIDATE>
	
Example call:
	
	python o2rmeta.py -debug validate -s schema/json/o2r-meta-schema.json -c broker/tests/metadata_o2r.json

Explanation of the switches:

+ `-s` <SCHEMA> : required path or URL to the schema file, can be json or xml.
+ `-c` <CANDIDATE> : required path to candidate that shall be validated.

# (4) Harvester tool:

Collects OAI-PMH metadata from catalogues, data registries and repositories and parses them to assist the completion of a metadata set.
_Note, that this tool is currently only a demo._ 

	python o2rmeta.py harvest -e <ELEMENT> -q <QUERY>
	
Example call:
	
	python o2rmeta.py -debug harvest -e"doi" -q"10.14457/CU.THE.1989.1"

Explanation of the switches:

+ `-e` <ELEMENT> : MD element type for search, e.g. _doi_ or _creator_
+ `-q` <QUERY> : MD content to start the search

# Adding new parsers

## Introduction

The extractor tool uses Python classes as parser modules.
Each parser can process specific formats and the full list of supported file formats can be retrieved via CLI (see above).

In order to add a new custom parser, you have to write a parser class and add it to the parser directory.

Note that [future versions](https://github.com/o2r-project/o2r-meta/issues/95) of o2r-meta might be able to register all parsers based on the files in the `parsers` directory.
Until then it is necessary to register a new parser in the extractor script

The use of classes as parsers is currently implemented in a rather naïve way.
However, in order to be able to take advantage of non static methods, all parsers are designed as classes already.

The general process of parsing is the following:

1. the parser accesses a target file, which was encountered by the extractor during a recursive scan of the target directory and identified based on the file extension
2. the target file is read and processed by a specific parser
3. the results of the processing are written to a dictionary data structure that is globally known to the program; the structure of the data dictionary is implicitly defined in `metaextract.py` and can be seen in `dummy.json`

## Structure of your parser Python class

_In this example we will call your new parser file `parse_abc.py` and the class in that file `ParseAbc`._

Here is a commented template for your parser file:

```python
# Class name keyword to signal availability to importing files
__all__ = ['ParseAbc']

# Optionally import the o2r-meta helping functions if want to have access to them
from helpers.helpers import *

# Import further external modules you would need and also add them to the requirements.txt file!
import myABC

# If (some of) the formats you want to parse depend on a successful import of external modules, which might be missing, use the following structure to support as much formats as possible
try:
    from myABC import *
    FORMATS = ['.abc']
except ImportError as iexc:
    FORMATS = []
    availability_issues = str(iexc)

# The identifying name of your parser
ID = 'o2r meta abc parser'

# Declare your class
class ParseAbc:
    # Required method to return the ID
    @staticmethod
    def get_id():
        return str(ID)

    # Required method to return the available formats of this parser
    @staticmethod
    def get_formats():
        if not FORMATS:
            # Status notes are available via the helpers module
            status_note([__class__, ' unavailable (', str(availability_issues), ')'])
        return FORMATS

    # Required method. This is the place for your actual parsing code
    @staticmethod
    def parse(**kwargs):
        is_debug = False
        try:
            # The extractor provides the path of your target file
            path_file = kwargs.get('p', None)
            # And the metadata dictionary to which you want to write
            MASTER_MD_DICT = kwargs.get('md', None)
            is_debug = kwargs.get('is_debug', None)
            # Fictional example to add parsed data
            my_parsed_data = myABC.Dataset(path_file)
            my_return = {path_file: {}}
            my_return[path_file].update(my_parsed_data)
            if 'ABC' in MASTER_MD_DICT:
                if 'abc_files' in MASTER_MD_DICT['ABC']:
                    MASTER_MD_DICT['ABC']['abc_files'].append(my_return)
            return MASTER_MD_DICT
        except Exception as exc:
            status_note(str(exc), d=is_debug)
            return 'error'
```

## Steps to integrate your own parser

+ save a copy of your parser file `parse_abc.py` at `o2r-meta\parsers`
+ open `o2r-meta\extract\metaextract.py` and find the function `register_parsers`
+ add the following to that function using your own filename and class name:

```python
# From your file import your class
from parsers.parse_abc.py import ParseAbc
# To global list of parsers add an instance of your class
PARSERS_CLASS_LIST.append(ParseAbc())
```

+ test if the extractor recognizes your new parser by calling

```bash
python o2rmeta.py -debug extract -f
```

That's it, well done!
Now make a pull request and add your parser to o2r-meta, if you want to.

# Testing

Tests are implemented using [pytest](https://pytest.org) following [its conventions for test discovery](https://docs.pytest.org/en/latest/goodpractices.html#test-discovery).
The configuration file is `pytest.ini`.

The tests work 

```bash
pip install -U pytest

pytest

# run specific file and verbose output
pytest -vv --tb=long extract/tests/test_extract_offline.py

# show logging output live (not to be combined with -vv)
pytest -s

# re-run failed tests (--lf) or failed first (--ff)
pytest --last-failed
pytest --failed-first
```

A working launch configuration for vscode to debug the tests is

´´´json
{
	"name": "Python: Tests (integrated terminal)",
	"type": "python",
	"request": "launch",
	"stopOnEntry": true,
	"pythonPath": "/usr/bin/python3",
	"program": "/usr/local/bin/pytest",
	"cwd": "${workspaceFolder}",
	"console": "integratedTerminal",
	"env": {},
	"debugOptions": [],
	"internalConsoleOptions": "neverOpen"
}
```
