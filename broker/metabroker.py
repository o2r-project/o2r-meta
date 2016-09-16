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

import argparse
import csv
import json
import os
import sys
from xml.dom import minidom

import dicttoxml


def translate(category, input_element):
    # read crosswalk matrix for translation of element names
    csvfile = open(crosswalk, 'r')
    reader = csv.DictReader(csvfile, columns, delimiter=',')
    for row in reader:
        output_element = ''
        if input_element == row['raw']:
            output_element = row[category]
            break
    if len(output_element) > 0 and output_element != '-':
        return output_element
    else:
        return None

def do_broker(inputfile, outputdir):
    print('[metabroker] processing ' + inputfile)
    # load raw metadata file
    with open(inputfile) as data_file:
        input_dict = json.load(data_file)
    # create translation for each schema category
    for this in columns:
        if this == 'Concept' or this == 'raw': continue
        data_dict = {}
        for key in input_dict:
            translated = translate(this, str(key))
            if translated:
                data_dict.update({translated: input_dict[key]})
        # save results
        save_output(data_dict, 'json', file[6:-5] + '_' + this)
        save_output(data_dict, 'xml', file[6:-5] + '_' + this)


def save_output(data_dict, format, file_name):
    if format == 'json':
        output_data = json.dumps(data_dict, sort_keys=True, indent=4, separators=(',', ': '))
    elif format == 'xml':
        output_data = minidom.parseString(dicttoxml.dicttoxml(data_dict)).toprettyxml(indent='\t')
    output_filename = os.path.join(output_dir,file_name + '.' + format)
    with open(output_filename, 'w', encoding='utf-8') as outfile:
        outfile.write(output_data)
    print('[metabroker] ' + str(os.stat(output_filename).st_size) + ' bytes written to ' + os.path.abspath(output_filename))

# main:
if __name__ == "__main__":
    if sys.version_info[0] < 3:
        # py2
        print('[metabroker] requires py3k or later')
        sys.exit()
    else:
        # py3k
        print('[metabroker] initializing')
        # process files in target directory
        parser = argparse.ArgumentParser(description='description')
        parser.add_argument('-i', '--inputdir', help='input directory', required=True)
        parser.add_argument('-o', '--outputdir', help='output directory for extraction docs', required=True)
        #parser.add_argument('-s', '--outputtostdout', help='output the result of the extraction to stdout', action='store_true', default=False)
        args = parser.parse_args()
        argsdict = vars(args)
        input_dir = argsdict['inputdir']
        output_dir = argsdict['outputdir']
        #output_to_console = argsdict['outputtostdout']
        # check args
        if not os.path.isdir(input_dir):
            print('[metabroker] ! error, input dir "'+ input_dir + '" does not exist')
            sys.exit()
        else: pass
        #if not os.path.isdir(output_dir):
        #   print('[metabroker] directory"' + output_dir + '"  will be created during extraction...')
        crosswalk = 'crosswalk.csv'
        columns = ['Concept', 'raw', 'o2r', 'CodeMeta', 'DataCite', 'RADAR']
        print('[metabroker] using ' + crosswalk)
        # process all files in input directory
        for file in os.listdir(input_dir):
            if file.lower().startswith('meta_'):
                if file.lower().endswith('.json'):
                    do_broker(os.path.join(input_dir, file), output_dir)
                elif file.lower().endswith('.xml'):
                    # to do: xml input processing
                    pass
            else:
                pass
        print('[metabroker] done')