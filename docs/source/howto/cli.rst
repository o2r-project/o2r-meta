
Command-Line Interface (CLI)
============================

Usage
^^^^^
When calling o2r meta, you can chose from the following commands, each representing one tool of the o2r meta suite: *extract*, *validate*, *broker* and *harvest*.

::

   o2r-meta [-debug] extract|validate|broker|harvest <ARGS>

Options:

* ``-debug`` : option to enable raise error and provide verbose debug info where applicable


Extractor
^^^^^^^^^

Collect meta information from files in a workspace.

::

   o2rmeta extract -i <INPUT_DIR> -s|-o <OUTPUT_DIR> [-xo] [-m] [-xml] [-ercid <ERC_ID>]

with

* ``-f`` returns a list of supported file formats (extensions) and terminates program
* ``-i`` <INPUT_DIR> : starting path for recursive search for parsable files
* ``-s:`` option to print out results to console. This switch is mutually exclusive with ``-o``. At least one of them must be given
* ``-o`` <OUTPUT_DIR> : output path, where data should be saved. If the directory does not exist, it will be created on runtime.  This switch is mutually exclusive with -s. At least one of them must be given.
* ``-xo`` : option to disable http requests (the extractor will stay offline. This disables orcid retrieval, erc spec download, doi retrieval, ...)
* ``-m`` : option to additionally enable individual output of all processed files.
* ``-lic``: option to configure the default metadata license.
* ``-xml`` : option to change output format from json (default) to xml.
* ``-ercid`` <ERC_ID>: option to provide an ERC identifier.
* ``-b`` <BASE_DIR>: option to provide starting point directory for relative paths output

Example call:

::

   o2r-meta -debug extract -i extract/tests -o extract/tests -xo
   

Broker
^^^^^^

This tool translate metadata from o2r to third party schemas. The broker has two modes: In **mapping mode**, it creates fitting metadata for a given map by following a translation scheme included in that mapping file. In **checking mode** it returns missing metadata information for a target service or plattform, e.g. zenodo publication metadata, for a given checklist and input data.

The broker can be used to translate between different standards for metadata sets. A typical workflow would look as follows:

#. Convert extracted raw metadata to o2r schema compliant metadata. 
#. Convert o2r metadata to a 3rd party repository schema, e.g. zenodo.

Each Step can be done with a single call of the broker. Translation instructions as well as checklists are stored in json formatted map files, documented `here`_

.. _here: https://github.com/o2r-project/o2r-meta/blob/master/test/schema/docs/mappings_docs.md

::

  o2r-meta broker -i <INPUT_FILE> -c <CHECKLIST_FILE>|-m <MAPPING_FILE> -s|-o <OUTPUT_DIR>

whith

* ``-c`` <CHECKLIST_FILE> : required path to a json checklist file that holds checking instructions for the metadata. This switch is mutually exclusive with ``-m``. At least one of them must be given.
* ``-m`` <MAPPING_FILE> : required path to a json mapping file that holds translation instructions for the metadata mappings. This switch is mutually exclusive with ``-c``. At least one of them must be given.
* ``-i`` <INPUT_FILE> : path to input json file.
* ``-s``: option to print out results to console. This switch is mutually exclusive with ``-o``. At least one of them must be given.
* ``-o`` <OUTPUT_DIR> : required output path, where data should be saved. If the directory does not exist, it will be created on runtime. This switch is mutually exclusive with ``-s``. At least one of them must be given.

Example calls:
::

   o2r-meta -debug broker -c broker/checks/zenodo-check.json -i schema/json/example_zenodo.json -o broker/tests/all

   o2r-meta -debug broker -m broker/mappings/zenodo-map.json -i broker/tests/metadata_o2r.json -o broker/tests/all

Supported checks/maps
#####################
=============  ========================  ======================  ========  =======================================
  Service      Checklist file             mapping file            status   comment 
=============  ========================  ======================  ========  =======================================
zenodo         zenodo-check.json         zeonodo-map.json          WIP      zenodo will register MD @ datacite.org
eudat b2share  eudat-b2share-check.json  eudat-b2share-map.json     WIP      b2share supports custom MD schemas

=============  ========================  ======================  ========  =======================================

Additionally the following features will be made available in the future:

* Documentation of the formal map-file "minimal language" (create your own map-files).
* Governing JSON-Schema for the map files (validate map-files against the map-file-schema).

Validator
^^^^^^^^^
This tool check if metadata set is valid to the schema.

::

   o2r-meta validate -s <SCHEMA> -c <CANDIDATE>

with 

* ``-s`` : required path or URL to the schema file, can be json or xml.
* ``-c`` : required path to candidate that shall be validated.

Example call:

::

    o2r-meta -debug validate -s schema/json/o2r-meta-schema.json -c broker/tests/metadata_o2r.json


Harverst
^^^^^^^^

This tool collects OAI-PMH metadata from catalogues, data registries and repositories and parses them to assist the completion of a metadata set. Note, that this tool is **currently only a demo**.

::

  o2r-meta harvest -e <ELEMENT> -q <QUERY>

with 

* ``-e``: MD element type for search, e.g. doi or creator
* ``-q`` : MD content to start the search

Example call:

::

   o2r-meta -debug harvest -e"doi" -q"10.14457/CU.THE.1989.1"


