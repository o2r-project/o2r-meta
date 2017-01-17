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
import datetime
import xml.etree.ElementTree as ET
from xml.dom import minidom


def do_outputs(output_data, out_mode, out_name, file_ext):
    if out_mode == '@s':
        # give out to screen
        print(output_data)
    elif out_mode == '@none':
        # silent mode
        pass
    else:
        try:
            # output path is given in <out_mode>
            output_filename = os.path.join(out_mode, ''.join((out_name, file_ext)))
            if not os.path.exists(out_mode):
                os.makedirs(out_mode)
            with open(output_filename, 'w', encoding='utf-8') as outfile:
                if file_ext == '.json':
                    output_data = json.dumps(output_data, sort_keys=True, indent=4, separators=(',', ': '))
                outfile.write(str(output_data))
            status_note(''.join(
                (str(os.stat(output_filename).st_size), ' bytes written to ', os.path.abspath(output_filename))))
        except Exception as exc:
            status_note(''.join(('! error while creating outputs: ', exc.args[0])))


def map_json(element, value, map_data, output_dict):
    # parse complete map, find out how keys translate to target schema
    if element in map_data:
        # prepare types:
        if map_data[element]['parent'] != 'root':
            pass
        else:
            # most simple 1:1
            if map_data[element]['type'] == 'string':
                output_dict[map_data[element]['translatesTo']] = value
        if map_data[element]['type'] == 'array':
            # e. g. author array (is list in py)
            output_dict[map_data[element]['translatesTo']] = []
    if type(value) is list or type(value) is dict:
        # list of keys, nestedness:
        c = 0
        for key in value:
            # ---<key:string>----------------------------------------------
            if type(key) is str:
                if key in map_data:
                    d = 0
                    # ---<subkey:string>----------------------------------------------
                    if type(value[key]) is list:
                        for sub_list_key in value[key]:
                            # ---<subkey:string>----------------------------------------------
                            if type(sub_list_key) is str:
                                # e.g. keywords as list of string
                                output_dict[map_data[key]['translatesTo']] = value[key]
                            # ---<subkey:dictionary>------------------------------------------
                            elif type(sub_list_key) is dict:
                                # as for r_code_block#Dependency#text
                                temp = {}
                                for subsub_list_key in sub_list_key:
                                    if subsub_list_key in map_data:
                                        location = map_data[subsub_list_key]['parent']
                                        temp[map_data[subsub_list_key]['translatesTo']] = value[key][d][subsub_list_key]
                                    else:
                                        continue
                                # now add to results under the appropriate key:
                                d += 1
                                if location:
                                    try:
                                        output_dict[location].append(temp)
                                        pass
                                    except:
                                        output_dict[location] = []
                                        output_dict[location].append(temp)
                                else:
                                    output_dict[location] = []
            # ---<key:list>----------------------------------------------
            elif type(key) is list:
                for y in key:
                    if y in map_data:
                        # to do: fix 'parent' to 'translatesTo'
                        if output_dict[map_data[y]['parent']]:
                            output_dict[map_data[y]['parent']].append(value[c][y])
            # ---<key:dict>----------------------------------------------
            elif type(key) is dict:
                # as for 'authors'
                location = ''
                temp = {}
                for sub_dict_key in key:
                    if sub_dict_key in map_data:
                        location = map_data[sub_dict_key]['parent']
                        temp[map_data[sub_dict_key]['translatesTo']] = value[c][sub_dict_key]
                # to do: error handler if location empty or output misses the key
                output_dict[location].append(temp)
            else:
                pass
            c += 1
    return output_dict


def map_xml(element, value, map_data, xml_root):
    a = None
    try:
        if type(value) is list or type(value) is dict:
            status_note(''.join(('unfolding key <', str(element),'>')))
            if str(element) in map_data:
                fields = map_data[element]
                fieldslist = fields.split(seperator)
                # nestification along pseudo xpath from map data
                for field in fieldslist:
                    # pseudo xpath has no divisions:
                    if len(fieldslist) == 1:
                        a = ET.SubElement(xml_root, field)
                        a.text = value
                        break
                    # element has been created in former loop circle because pseudo xpath has divisions:
                    if a is not None: # do not change to "if a:". needs safe test for xml element class
                        # insert content values from metadata in innermost element, i.e. last division in pseudo xpath
                        if field == fieldslist[-1]:
                            # in case the elements features is a list of lists:
                            for key in value:
                                if type(key) is list or type(key) is dict:
                                    status_note('unfolding subkey list')
                                    c = ET.SubElement(a, field)
                                    for subkey in key:
                                        if ''.join(subkey) in map_data:
                                            d = ET.SubElement(c, map_data[subkey])
                                            d.text = key[subkey]
                                elif type(key) is str:
                                    # simple lists added to element:
                                    b = ET.SubElement(a, field)
                                    b.text = key
                                else:
                                    continue
                    # all other cases (no element with this name created yet)
                    else:
                        a = ET.SubElement(xml_root, field)
                return xml_root
            # element is not in map data:
            else:
                status_note(''.join(('skipping nested key <', str(element), '> (not in map)')))
        # value from metadata is simple, i.e. not nested, no list, no dictionary, just string:
        elif type(value) is str:
            if element in map_data:
                fields = map_data[element]
                fieldslist = fields.split(seperator)
                # nestification along pseudo xpath from map data
                for field in fieldslist:
                    if len(fieldslist) == 1:
                        a = ET.SubElement(xml_root, field)
                        a.text = value
                        break
                    if a is not None: # do not change to "if a:". needs safe test for xml element class
                        a = ET.SubElement(a, field)
                        #insert content in innermost node, i.e. last in mapping pseudo xpath
                        if field == fieldslist[-1]:
                            a.text = value
                    else:
                        #attach to given super element
                        a = ET.SubElement(xml_root, field)
                return xml_root
            else:
                status_note(''.join(('skipping key <', element, '> (not in map)')))
        else:
            status_note('unknown data type in key')
    except:
        status_note('! error while mapping xml')
        raise


def status_note(msg):
    print(''.join(('[o2rmeta][broker] ', msg)))


# Main
def start(**kwargs):
    input_dir = kwargs.get('i', None)
    output_dir = kwargs.get('o', None)
    output_to_console = kwargs.get('s', None)
    seperator = '#' #<-- make this generic
    my_map = kwargs.get('m', None)
    # output mode
    if output_to_console:
        output_mode = '@s'
    elif output_dir:
        output_mode = output_dir
        if not os.path.isdir(output_dir):
            status_note(''.join(('directory at <', output_dir, '> will be created during extraction...')))
    else:
        # not possible currently because output arg group is on mutual exclusive
        output_mode = '@none'

    # open map file and find out mode
    try:
        with open(my_map, encoding='utf-8') as data_file:
            map_file = json.load(data_file)
            settings_data = map_file['Settings']
            map_data = map_file['Map']
            my_mode = settings_data['mode']
    except:
        raise
    # distinguish format for output
    if my_mode == 'json':
        # try parse all possible metadata files:
        for file in os.listdir(input_dir):
            if os.path.basename(file).startswith('metadata_'):
                json_output = {}
                with open(os.path.join(input_dir, file), encoding='utf-8') as data_file:
                    test_data = json.load(data_file)
                for element in test_data:
                    try:
                        map_json(element, test_data[element], map_data, json_output)
                    except:
                        raise
                ##do_outputs(json_output, output_mode, 'o2r_'+os.path.splitext(file)[0], '.json')
                do_outputs(json_output, output_mode, settings_data['outputfile'], '.json')
    elif my_mode == 'txt':
        # to do: handle txt based maps like bagit
        txt_output = ''
        do_outputs(txt_output, output_mode, '.txt')
    elif my_mode == 'xml':
        root = ET.Element(settings_data['root'])
        # to do: generify for complex xml maps
        root.set('xmlns', settings_data['root@xmlns'])
        root.set('xmlns:xsi', settings_data['root@xmlns:xsi'])
        root.set('xsi:schemaLocation', settings_data['root@xsi:schemaLocation'])
        with open(os.path.join('tests', 'meta_test1.json'), encoding='utf-8') as data_file:
            test_data = json.load(data_file)
        for element in test_data:
            try:
                map_xml(element, test_data[element], map_data, root)
            except:
                raise
        output = ET.tostring(root, encoding='utf8', method='xml')
        do_outputs(minidom.parseString(output).toprettyxml(indent='\t'), output_mode, '.xml')
    else:
        status_note('! error: cannot process map mode of <' + my_map + '>')
