"""
    Copyright (c) 2016 - o2r project

    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at

        http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.

"""

import argparse
import json
import os
import sys

import jsonschema
import requests
from lxml import etree


def json_validate(c, s, bln_c_http, bln_s_http):
    try:
        if bln_s_http:
            r = requests.get(s)
            schema = json.loads(r.text)
        else:
            with open(os.path.abspath(s), encoding='utf-8') as schema_file:
                schema = json.load(schema_file)
        if bln_c_http:
            r = requests.get(c)
            candidate = json.loads(r.text)
        else:
            with open(os.path.abspath(c), encoding='utf-8') as candidate_file:
                candidate = json.load(candidate_file)
        jsonschema.validate(candidate, schema)
        status_note('valid: ' + c)
    except jsonschema.exceptions.ValidationError as exc:
        status_note('!invalid: ' + str(exc))
        #raise
    except:
        status_note('!error: ' + str(sys.exc_info()[0]))
        #raise


def xml_validate(c, s, bln_c_http, bln_s_http):
    try:
        if bln_s_http:
            schema = etree.parse(s)
        else:
            with open(os.path.abspath(s), encoding='utf-8') as schema_file:
                schema = etree.parse(schema_file)
        if bln_c_http:
            candidate = etree.parse(c)
        else:
            with open(os.path.abspath(c), encoding='utf-8') as candidate_file:
                candidate = etree.parse(candidate_file)
        xmlschema = etree.XMLSchema(schema)
        if xmlschema(candidate):
            status_note('valid: ' + os.path.basename(c))
        else:
            status_note('invalid: ' + os.path.basename(c))
    except etree.XMLSchemaParseError as exc:
        status_note('!error: ' + str(exc))
        #raise
    except:
        status_note('!error: ' + str(sys.exc_info()[0]))
        #raise


def status_note(msg):
    print(''.join(('[metavalidate] ', msg)))


# main
if __name__ == "__main__":
    if sys.version_info[0] < 3:
        # py2
        status_note('requires py3k or later')
        sys.exit()
    else:
        parser = argparse.ArgumentParser(description='description')
        parser.add_argument('-s', '--schema', help='path to schema', type=str, required=True)
        parser.add_argument('-c', '--candidate', help='path to candidate', type=str, required=True)
        args = parser.parse_args()
        argsdict = vars(args)
        my_schema = argsdict['schema']
        my_candidate = argsdict['candidate']
        status_note('checking ' + os.path.basename(my_candidate) + ' against ' + os.path.basename(my_schema))
        if my_candidate.endswith('.json'):
            json_validate(my_candidate, my_schema, my_candidate.startswith('http'), my_schema.startswith('http'))
        elif my_candidate.endswith('.xml'):
            xml_validate(my_candidate, my_schema, my_candidate.startswith('http'), my_schema.startswith('http'))
        else:
            status_note('!warning, could not process this type of file')
            sys.exit()
