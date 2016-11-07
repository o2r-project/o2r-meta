'''
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

'''

#import argparse
import json
import os
import sys
from xml.dom import minidom

import xml.etree.ElementTree as ET



def map_this(element, value, map_data, xml_root):
    a = None
    try:
        if type(value) is list or type(value) is dict:
            print('[metabroker] unfolding key <' + str(element) +'>')
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
                                    print('[metabroker] unfolding subkey list')
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
                print('[metabroker] skipping nested key <' + str(element) + '> (not in map)')
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
                print('[metabroker] skipping key <'+ element + '> (not in map)')
        else:
            print('[metabroker] unknown data type in key')
    except:
        print('[metabroker] mapping error')
        raise

#Main
if __name__ == "__main__":
    if sys.version_info[0] < 3:
        # py2
        print('[metabroker] requires py3k or later')
        sys.exit()
    else:
        # init
        seperator = '#' #<-- make this generic
        # to do: transform o2r raw extraced to o2r schema using o2r-map.json
        #try:
        #    with open(os.path.join('mappings', 'o2r-map.json'), encoding='utf-8') as data_file:
        #    ...
        #except:
        #    raise
        # ------ XML maps ------
        # load map for datacite
        try:
            with open(os.path.join('mappings', 'datacite-map.json'), encoding='utf-8') as data_file:
                map_datacite_data = json.load(data_file)
                settings_data = map_datacite_data['Settings']
                map_data = map_datacite_data['Map']
            root = ET.Element(settings_data['root'])
            root.set('xmlns', settings_data['root@xmlns'])
            root.set('xmlns:xsi', settings_data['root@xmlns:xsi'])
            root.set('xsi:schemaLocation', settings_data['root@xsi:schemaLocation'])
        except:
            raise
        # test o2r output meta
        with open(os.path.join('tests', 'meta_test1.json'), encoding='utf-8') as data_file:
            test_data = json.load(data_file)
        for element in test_data:
            try:
                map_this(element, test_data[element], map_data, root)
            except:
                # raise
                continue
        output = ET.tostring(root, encoding='utf8', method='xml')
        print(minidom.parseString(output).toprettyxml(indent='\t'))