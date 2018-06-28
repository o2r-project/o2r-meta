"""
    Copyright (c) 2016-2018 - o2r project

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
import re
import sys
import datetime
import xml.etree.ElementTree as ElT
from xml.dom import minidom
from helpers.helpers import *
from filelock import Timeout, SoftFileLock


def check(checklist_pathfile, input_json):
    # checks which required fields are already fulfilled by a given set of metadata
    status_note(['processing ', input_json], d=is_debug)
    # prepare input filepath
    try:
        if os.path.isfile(input_json):
            with open(input_json, encoding='utf-8') as data_file:
                input_data = json.load(data_file)
            # open checklist file and find out mode
            output_dict = {'required': []}
            with open(checklist_pathfile, encoding='utf-8') as data_file:
                check_file = json.load(data_file)
                settings_data = check_file['Settings']  # json or xml
                checklist_data = check_file['Checklist']
                #my_mode = settings_data['mode']
                # todo:
                #check_data_conditions = check_file['Conditions']
                for x in checklist_data:
                    if x not in input_data:
                        output_dict['required'].append(x)
                do_outputs(output_dict, output_dir, settings_data['outputfile'])
    except:
        raise


def do_outputs(output_data, out_mode, out_name):
    if out_mode == '@s':
        # give out to screen
        print(output_data)
    elif out_mode == '@none':
        # silent mode
        pass
    else:
        try:
            # output path is given in <out_mode>
            output_filename = os.path.join(out_mode, out_name)
            if not os.path.exists(out_mode):
                os.makedirs(out_mode)
            with open(output_filename, 'w', encoding='utf-8') as outfile:
                # for json:
                output_data = json.dumps(output_data, sort_keys=True, indent=4, separators=(',', ': '))
                outfile.write(str(output_data))
                # for xml:
                # todo: xml

            status_note([str(os.stat(output_filename).st_size), ' bytes written to ', os.path.abspath(output_filename)], d=is_debug)
            # update meta meta for archival:
            update_archival(out_mode)
        except Exception as exc:
            raise
            status_note(['! error while creating outputs: ', exc.args[0]], d=is_debug)


def update_archival(outpath):
    #add information to "package slip" meta meta data

    infofile = os.path.join(outpath, "package_slip.json")
    infofile_lock = os.path.join(outpath, "package_slip.json.lock")
    lock_timeout = 5
    lock = SoftFileLock(infofile_lock)

    try:
        with lock.acquire(timeout=lock_timeout):
            if os.path.isfile(infofile):
                # file exists, needs update
                status_note(['Going to update ', infofile], d=is_debug)
                with open(infofile, encoding='utf-8') as data_file:
                    data = json.load(data_file)
                    found = False
                    for key in data['standards_used']:
                        if key == archival_info['standards_used'][0]:
                            found = True
                    if not found:
                        data['standards_used'].append(archival_info['standards_used'][0])
            else:
                # file does not exist, needs to be created
                data = archival_info
            
            # in any case: write current data back to info file
            status_note(['Write info to ', infofile], d=is_debug)
            with open(infofile, 'w', encoding='utf-8') as outfile:
                # for json:
                output_data = json.dumps(data, sort_keys=True, indent=4, separators=(',', ': '))
                outfile.write(str(output_data))
                status_note([str(os.stat(infofile).st_size), ' bytes written to ', os.path.abspath(infofile)], d=is_debug)
    except Timeout:
        status_note(['Cannot acquire lock within ', lock_timeout, ' seconds, raising exception!'], d=is_debug)
        raise
    except Exception as exc:
        status_note(str(exc), d=is_debug)
        raise
    finally:
        lock.release()



def map_json(element, value, map_data, output_dict):
    # parse complete map, find out how keys translate to target schema
    if element in map_data:
        # prepare types:
        status_note(['processing element <', str(element), '>'], d=is_debug)
        if map_data[element]['hasParent'] != 'root':
            pass
        else:
            # most simple 1:1
            if map_data[element]['type'] == 'string':
                output_dict[map_data[element]['translatesTo']] = value
        if map_data[element]['type'] == 'array':
            # e. g. author array (is list in py)
            # if input is str and output is array with same name, then just copy it as first in array
            if type(value) is str:
                #if re.match(r'[A-Za-z\s\.\-]*', value):
                output_dict[map_data[element]['translatesTo']] = [value]
            else:
                output_dict[map_data[element]['translatesTo']] = []
    if type(value) is list or type(value) is dict:
        if type(value) is list:
        # plain list, as for keywords
            if element in map_data:
                allString = False
                for x in value:
                    # if all is plain string in that list, take whole list
                    if type(x) is str:
                        allString = True
                    else:
                        allString = False
                if allString == True:
                    output_dict[map_data[element]['translatesTo']] = value
        # list of keys, nestedness:
        c = 0
        for key in value:
            # ---<key:string>----------------------------------------------
            if type(key) is str:
                if key in map_data:
                    # special case create new entry based on sub element:
                    if map_data[key]['type'] == 'new':
                        if map_data[key]['hasParent'] != key and map_data[key]['needsParent'] == "root":
                            output_dict[map_data[key]['translatesTo']] = value[key]
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
                                        location = map_data[subsub_list_key]['needsParent']
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
                        if output_dict[map_data[y]['hasParent']]:
                            output_dict[map_data[y]['needsParent']].append(value[c][y])
            # ---<key:dict>----------------------------------------------
            elif type(key) is dict:
                # e.g. for 'authors'
                location = ''
                temp = {}
                if type(key) is dict:
                    for sub_dict_key in key:
                        if sub_dict_key in map_data:
                            # check if this is the right key (possible same name of keys of different parents)
                            if map_data[sub_dict_key]['hasParent'] == element:
                                location = map_data[sub_dict_key]['needsParent']
                                temp[map_data[sub_dict_key]['translatesTo']] = value[c][sub_dict_key]
                    # to do: error handler if location empty or output misses the key
                    if location in output_dict:
                        output_dict[location].append(temp)
            else:
                pass
            c += 1
    return output_dict


def map_xml(element, value, map_data):
    global root
    seperator = '#'
    a = None
    try:
        if type(value) is list or type(value) is dict:
            status_note(['unfolding key <', str(element), '>'], d=False)
            if str(element) in map_data:
                fields = map_data[element]
                fieldslist = fields.split(seperator)
                # nestification along pseudo xpath from map data
                for field in fieldslist:
                    # pseudo xpath has no divisions:
                    if len(fieldslist) == 1:
                        a = ElT.SubElement(root, field)
                        a.text = value
                        break
                    # element has been created in former loop circle because pseudo xpath has divisions:
                    if a is not None:  # do not change to "if a:". needs safe test for xml element class
                        # insert content values from metadata in innermost element, i.e. last division in pseudo xpath
                        if field == fieldslist[-1]:
                            # in case the elements features is a list of lists:
                            for key in value:
                                if type(key) is list or type(key) is dict:
                                    status_note('unfolding subkey list', d=is_debug)
                                    c = ElT.SubElement(a, field)
                                    for subkey in key:
                                        if subkey in map_data:
                                            d = ElT.SubElement(c, map_data[subkey])
                                            d.text = key[subkey]
                                elif type(key) is str:
                                    # simple lists added to element:
                                    b = ElT.SubElement(a, field)
                                    b.text = key
                                else:
                                    continue
                    # all other cases (no element with this name created yet)
                    else:
                        a = ElT.SubElement(root, field)
                return root
            # element is not in map data:
            else:
                status_note(['skipping nested key <', str(element), '> (not in map)'], d=False)
        # value from metadata is simple, i.e. not nested, no list, no dictionary, just string:
        elif type(value) is str:
            if element in map_data:
                fields = map_data[element]
                fieldslist = fields.split(seperator)
                # nestification along pseudo xpath from map data
                sub_field = None
                for field in fieldslist:
                    if len(fieldslist) == 1:
                        sub_field = ElT.SubElement(root, field)
                        sub_field.text = value
                        break
                    if sub_field is not None:  # do not change to "if a:". needs safe test for xml element class
                        sub_field = ElT.SubElement(sub_field, field)
                        #insert content in innermost node, i.e. last in mapping pseudo xpath
                        if field == fieldslist[-1]:
                            sub_field.text = value
                    else:
                        #attach to given super element
                        sub_field = ElT.SubElement(root, field)
                return root
            else:
                status_note(['skipping key <', element, '> (not in map)'], d=is_debug)
        else:
            status_note('unknown data type in key', d=is_debug)
    except Exception as exc:
        raise
        status_note(['! error while mapping xml', str(exc)], d=is_debug)


# Main
def start(**kwargs):
    global is_debug
    is_debug = kwargs.get('dbg', None)
    global input_file
    input_file = kwargs.get('i', None)
    global output_dir
    output_dir = kwargs.get('o', None)
    output_to_console = kwargs.get('s', None)
    global my_check
    my_check = kwargs.get('c', None)
    global my_map
    my_map = kwargs.get('m', None)
    global archival_info
    archival_info = {'standards_used': []}
    global root
    # output mode
    if output_to_console:
        output_mode = '@s'
    elif output_dir:
        output_mode = output_dir
        if not os.path.isdir(output_dir):
            status_note(['directory at <', output_dir, '> will be created during extraction...'], d=is_debug)
    else:
        # not possible currently because output arg group is on mutual exclusive
        output_mode = '@none'
    if my_check is not None:
        check(my_check, input_file)
    if my_map is not None:
        # open map file and find out mode
        try:
            add_constant_values = {'const_list': []}
            with open(my_map, encoding='utf-8') as data_file:
                map_file = json.load(data_file)
                if 'Settings' in map_file:
                    settings_data = map_file['Settings']
                    map_data = map_file['Map']
                    my_mode = settings_data['mode']
                    if 'name' in settings_data:
                        archival_info['standards_used'].append({map_file['Settings']['name']: map_file['Settings']})
                        if 'output_file_prefix' in settings_data:
                            if 'version' in settings_data:
                                if 'output_file_extension' in settings_data:
                                    output_file_name = ''.join((settings_data['output_file_prefix'], '_', settings_data['name'], '_', settings_data['version'], settings_data['output_file_extension']))
                    if 'const' in settings_data:
                        for item in settings_data['const']:
                            add_constant_values['const_list'].append(item)
        except Exception as exc:
            status_note(str(exc), d=is_debug)
            raise
        if output_file_name is None:
            status_note(['! error: malformed mapping file <', my_map, '>'], d=is_debug)
            exit(1)
        # distinguish format for output
        if my_mode == 'json':
            # parse target file # try parse all possible metadata files:
            if not os.path.basename(input_file).startswith('metadata_'):
                status_note('Warning: inputfile does not look like a metadata file object', d=is_debug)
            json_output = {}
            for item in add_constant_values['const_list']:
                json_output.update(item)
            with open(os.path.join(input_file), encoding='utf-8') as data_file:
                input_data = json.load(data_file)
            for element in input_data:
                try:
                    map_json(element, input_data[element], map_data, json_output)
                except Exception as exc:
                    status_note(str(exc), d=is_debug)
                    raise
            do_outputs(json_output, output_mode, output_file_name)
        elif my_mode == 'txt':
            # to do: handle txt based maps like bagit
            txt_output = ''
            do_outputs(txt_output, output_mode, '.txt')
        elif my_mode == 'xml':
            root = ElT.Element(settings_data['root'])
            # to do: generify for complex xml maps
            root.set('xmlns', settings_data['root@xmlns'])
            root.set('xmlns:xs', settings_data['root@xmlns:xs'])
            root.set('xsi:schemaLocation', settings_data['root@xsi:schemaLocation'])
            with open(os.path.join(input_file), encoding='utf-8') as data_file:
                input_data = json.load(data_file)
            for element in input_data:
                try:
                    if element is not None:
                        if input_data[element] is not None:
                            map_xml(element, input_data[element], map_data)
                except:
                    raise
            output = ElT.tostring(root, encoding='utf8', method='xml')
            do_outputs(minidom.parseString(output).toprettyxml(indent='\t'), output_mode, output_file_name)
        else:
            status_note(['! error: cannot process map mode of <', my_map, '>'], d=is_debug)
