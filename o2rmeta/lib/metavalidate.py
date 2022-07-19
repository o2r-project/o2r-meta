"""
    Copyright (c) 2016, 2017 - o2r project

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
from .helpers_funct.helpers import *


def json_validate(c, s, bln_c_http, bln_s_http):
    global is_debug
    # process schema file file:
    try:
        schema = ''
        candidate = ''
        if bln_s_http:
            r = requests.get(s)
            schema = json.loads(r.text)
        else:
            with open(os.path.abspath(s), encoding='utf-8') as schema_file:
                schema = json.load(schema_file)
    except json.decoder.JSONDecodeError as jexc:
        status_note(['!error while parsing ', str(s), ': ', str(jexc)], d=is_debug)
    except jsonschema.exceptions.ValidationError as vexc:
        status_note(['!invalid: ', str(vexc)], d=is_debug)
    except Exception as exc:
        status_note(['!error: ', str(exc)], d=is_debug)
    # process candidate file:
    try:
        if bln_c_http:
            r = requests.get(c)
            candidate = json.loads(r.text)
        else:
            with open(os.path.abspath(c), encoding='utf-8') as candidate_file:
                candidate = json.load(candidate_file)
        jsonschema.validate(candidate, schema)
        status_note(['valid: ', c], d=False)
    except json.decoder.JSONDecodeError as jexc:
        status_note(['!error while parsing ', str(c), ': ', str(jexc)], d=is_debug)
    except jsonschema.exceptions.ValidationError as vexc:
        status_note(['!invalid: ', str(vexc)], d=is_debug)
    except Exception as exc:
        status_note(['!error: ', str(exc)], d=is_debug)


def xml_validate(c, s, bln_c_http, bln_s_http):
    global is_debug
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
            status_note(['valid: ', os.path.basename(c)])
        else:
            status_note(['invalid: ', os.path.basename(c)])
    except etree.XMLSchemaParseError as xexc:
        status_note(['! error: ', str(xexc)], d=is_debug)
    except Exception as exc:
        status_note(['! error: ', str(exc)], d=is_debug)


# main
def start(**kwargs):
    global is_debug
    is_debug = kwargs.get('dbg', None)
    schema_path = kwargs.get('s', None)
    candidate_path = kwargs.get('c', None)
    status_note(['checking ', os.path.basename(candidate_path), ' against ', os.path.basename(schema_path)], d=False)
    if candidate_path.endswith('.json'):
        json_validate(candidate_path, schema_path, candidate_path.startswith('http'), schema_path.startswith('http'))
    elif candidate_path.endswith('.xml'):
        xml_validate(candidate_path, schema_path, candidate_path.startswith('http'), schema_path.startswith('http'))
    else:
        status_note('! warning, could not process this type of file', e=True)
        sys.exit(1)
