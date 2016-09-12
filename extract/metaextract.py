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
import datetime
import json
import os
import re
import sys
from xml.dom import minidom

import dicttoxml
import yaml


def parse_yaml(input_text):
    yaml_data_dict = yaml.safe_load(input_text)
    # TO DO: Rename yaml keys according to our schema
    return yaml_data_dict

def parse_exobj(parameter):
    # to do
    # get these from live extraction results (o2rexobj.txt)
    result = ''
    return result

def parse_r(input_text):
    c = 0
    meta_r_dict = {}
    for line in input_text.splitlines():
        c += 1
        for rule in rule_set_r:
            this_rule = rule.split('\t')
            m = re.match(this_rule[2], line)
            if m:
                # dependency
                if this_rule[0] == 'Dependency':
                    # get these from live extraction results (o2rexobj.txt)
                    dep_os = parse_exobj('os')
                    dep_packetsys = 'https://cloud.r-project.org/'
                    dep_ver = parse_exobj('version')
                    segment = {'operatingSystem': dep_os, 'packageSystem': dep_packetsys, 'version': dep_ver, 'line': c, 'category': check_rpacks(m.group(1)), 'packageId': '{}'.format(m.group(1))}
                elif this_rule[0] == 'Output':
                    segment = {'feature': this_rule[1],'line': c, 'text': '{}'.format(m.group(1))}
                else:
                    segment = {'line': c, 'text': '{}'.format(m.group(1))}
                meta_r_dict.setdefault(this_rule[0], []).append(segment)
    return meta_r_dict

def check_rpacks(package):
    label = ''
    if package in open(packlist_geosci).read():
        label += 'geo sciences,'
    if package in open(packlist_crantop100).read():
        label += 'CRAN Top100,'
    if len(label) < 1:
        label = 'none,'
    return label[:-1]

# extract
def do_ex(my_pathfile, modus, extraction_files_dir, output_to_console, multiline, rule_set):
    c = 0
    output_data = None
    output_fileext = None
    # create data structure for multiline contexts
    # determine which infos best come from live extraction
    # to do: create args for path_to_liveex_logfile and papersource
    erc_id = ''
    papersource = ''
    data_dict = {'file': my_pathfile, 'ErcIdentifier': erc_id, 'GeneratedBy': 'metaextract.py', 'papersource': papersource}
    with open(os.path.relpath(my_pathfile), encoding='utf-8') as inpfile:
        content = inpfile.read()
        if multiline:
            # for rmd, yaml, etc.
            for rule in rule_set:
                this_rule = rule.split('\t')
                s = re.search(this_rule[1], content, flags=re.DOTALL)
                if s is not None:
                    if this_rule[0].startswith('yaml'):
                        data_dict.update(parse_yaml('{}'.format(s.group(1))))
                    if this_rule[0].startswith('rblock'):
                        data_dict['r_codeblock'] = ''
                        data_dict.update(r_codeblock = parse_r('{}'.format(s.group(1))))
        else:
            # parse entire file as one code block
            data_dict.update(r_codeblock = parse_r(content))
    # save results
    if modus == 'json':
        output_data = json.dumps(data_dict, sort_keys=True, indent=4, separators=(',', ': '))
        output_fileext = '.json'
    if modus == 'xml':
        output_data = minidom.parseString(dicttoxml.dicttoxml(data_dict)).toprettyxml(indent='\t')
        output_fileext = '.xml'
    timestamp = re.sub('\D', '', str(datetime.datetime.now().strftime('%Y%m%d%H:%M:%S.%f')[:-4]))
    output_filename = 'meta_' + timestamp + '_' + os.path.basename(my_pathfile)[:8].replace('.', '_') + output_fileext
    if extraction_files_dir:
        output_filename = os.path.join(extraction_files_dir, output_filename)
        if not os.path.exists(extraction_files_dir):
            os.makedirs(extraction_files_dir)
    with open(output_filename, 'w', encoding='utf-8') as outfile:
        outfile.write(output_data)
    print('[metaextract] ' + str(os.stat(output_filename).st_size) + ' bytes written to ' + os.path.abspath(output_filename))
    if output_to_console:
        print(output_data)

# main:
if __name__ == "__main__":
    if sys.version_info[0] < 3:
        #py2
        print('[metaextract] requires py3k or later')
        sys.exit()
    else:
        #py3k
        print('[metaextract] initializing...')
        # rule set for r, compose as: entry name TAB entry subname TAB regex
        rule_set_r = []
        rule_set_r.append('Comment\tXXXX\t' + r'#{1,3}\s*(.{1,})')
        rule_set_r.append('Comment\tcodefragment\t' + r'#{1,3}\s*(.*\=.*\(.*\))')
        rule_set_r.append('Comment\tcontact\t' + r'(.*[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.].*)')
        rule_set_r.append('Comment\turl\t' + r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')
        rule_set_r.append('Dependency\tinstalls\t' + r'install.packages\((.*)\)')
        rule_set_r.append('Dependency\tXXXX\t' + r'library\(\'?\"?([a-zA-Z\d\.]*)[\"\'\)]')
        rule_set_r.append('Dependency\tXXXX\t' + r'require\(\'?\"?([a-zA-Z\d\.]*)[\"\'\)]')
        rule_set_r.append('Input\tdataset\t' + r'data\..*\((.*)\)')
        rule_set_r.append('Output\tfile\t' + r'write\..*\((.*)\)')
        rule_set_r.append('Output\tresult\t' + r'(ggplot|plot|print)\((.*)\)')
        rule_set_r.append('Output\tsetseed\t' + r'set\.seed\((.*)\)')
        # rule set for rmd
        rule_set_rmd_multiline = []
        rule_set_rmd_multiline.append('yaml\t' + r'\-{3}(.*)[\.\-]{3}')
        rule_set_rmd_multiline.append('rblock\t' + r'\`{3}(.*)\`{3}')
        # other parameters
        packlist_crantop100 = 'list_crantop100.txt'
        packlist_geosci = 'list_geosci.txt'
        # process files in target directory
        parser = argparse.ArgumentParser(description='description')
        parser.add_argument('-i', '--inputdir', help='input directory', required=True)
        parser.add_argument('-m', '--modus', help='output format xml or json', required=True)
        parser.add_argument('-o', '--outputdir', help='output directory for extraction docs', required=True)
        parser.add_argument('-s', '--outputtostdout', help='output the result of the extraction to stdout', action='store_true', default=False)
        args = parser.parse_args()
        argsdict = vars(args)
        input_dir = argsdict['inputdir']
        output_modus = argsdict['modus']
        extraction_files_directory = argsdict['outputdir']
        output_to_console = argsdict['outputtostdout']
        for file in os.listdir(input_dir):
            if file.lower().endswith('.r'):
                do_ex(os.path.join(input_dir, file), output_modus, extraction_files_directory, output_to_console, False, rule_set_r)
            if file.lower().endswith('.rmd'):
                do_ex(os.path.join(input_dir, file), output_modus, extraction_files_directory, output_to_console, True, rule_set_rmd_multiline)
        print('[metaextract] done')