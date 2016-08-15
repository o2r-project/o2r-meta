import argparse
import json
import os
import re
import sys
from datetime import date
from xml.dom import minidom

import dicttoxml
import yaml


def parse_yaml(input_text):
    yaml_data_dict = yaml.safe_load(input_text)
    # TO DO: Rename yaml keys according to our schema
    return yaml_data_dict

def parse_r(input_text):
    c = 0
    meta_r_dict = {}
    for line in input_text.splitlines():
        c += 1
        for rule in rule_set_r:
            this_rule = rule.split('\t')
            m = re.match(this_rule[1], line)
            if m is not None:
                if this_rule[0].startswith('dependent'):
                    that_line = {'blockline': str(c), 'guess': check_rpacks(m.group(1)), 'text': '{}'.format(m.group(1))}
                    meta_r_dict.setdefault(this_rule[0], []).append(that_line)
                else:
                    that_line = {'blockline': str(c), 'text': '{}'.format(m.group(1))}
                    meta_r_dict.setdefault(this_rule[0], []).append(that_line)
    return meta_r_dict

def check_rpacks(package):
    if package in open(packlist_crantop100).read():
        return 'CRAN-top100'
    if package in open(packlist_geopack).read():
        return 'geo'
    else:
        return 'none'

#extract
def do_ex(my_pathfile, modus, extraction_files_dir, output_to_console, multiline, rule_set):
    c = 0
    output_data = None
    output_fileext = None
    # create data structure for multiline contexts
    data_dict = {'file': my_pathfile, 'generator': 'metaextract.py'}
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
    output_filename = 'metaex_' + os.path.basename(my_pathfile)[:8].replace('.', '_') + '_' + str(date.today()) + output_fileext
    if extraction_files_dir:
        output_filename = os.path.join(extraction_files_dir, output_filename)
        if not os.path.exists(extraction_files_dir):
            os.makedirs(extraction_files_dir)

    with open(output_filename, 'w', encoding='utf-8') as outfile:
        outfile.write(output_data)
    print(str(os.stat(output_filename).st_size) + ' bytes written to ' + os.path.abspath(output_filename))
    if output_to_console:
        print(output_data)

# Main:
if __name__ == "__main__":
    if sys.version_info[0] < 3:
        #py2
        print('requires py3k or later')
        sys.exit()
    else:
        #py3k
        #-i"tests" -o"json"
        parser = argparse.ArgumentParser(description='description')
        parser.add_argument('-i', '--input', help='input dir', required=True)
        parser.add_argument('-o', '--output', help='output format xml or json', required=True)
        parser.add_argument('-e', '--extractsdir', help='output directory for extraction docs', default='')
        parser.add_argument('-s', '--outputtostdout', help='output the result of the extraction to stdout', default = False)
        args = parser.parse_args()
        argsdict = vars(args)
        print('initializing...')
        # enter rules for r
        rule_set_r = []
        rule_set_r.append('comment\t' + r'#{1,3}\s*(.{1,})')
        rule_set_r.append('comment_codefragment\t' + r'#{1,3}\s*(.*\=.*\(.*\))')
        rule_set_r.append('comment_contact\t' + r'(.*[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.].*)')
        rule_set_r.append('comment_url\t' + r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')
        rule_set_r.append('dependent_installs\t' + r'install.packages\((.*)\)')
        rule_set_r.append('dependent_library\t' + r'library\(\'?\"?([a-zA-Z\d\.]*)[\"\'\)]')
        rule_set_r.append('dependent_require\t' + r'require\(\'?\"?([a-zA-Z\d\.]*)[\"\'\)]')
        rule_set_r.append('input_dataset\t' + r'data\..*\((.*)\)')
        rule_set_r.append('output_file\t' + r'write\..*\((.*)\)')
        rule_set_r.append('output_result\t' + r'(ggplot|plot|print)\((.*)\)')
        rule_set_r.append('output_setseed\t' + r'set\.seed\((.*)\)')
        rule_set_rmd_multiline = []
        rule_set_rmd_multiline.append('yaml\t' + r'\-{3}(.*)[\.\-]{3}')
        rule_set_rmd_multiline.append('rblock\t'+ r'\`{3}(.*)\`{3}')
        #rule_set_rmd = []
        #rule_set_rmd.append(r'\-{3}(.*)[\.\-]{3}') #re.DOTALL re.MULTILINE
        # rule_set_rmd.append('author\t' + r'\@?author\:\s\"(.*)\"')
        # rule_set_rmd.append('codeblock_start\t' + r'\`\`\`\{(.*)\}')
        # rule_set_rmd.append('related_file_knitr\t' + r'knitr\:\:read\_chunk\([\"\'](.*)[\"\']\)')
        # rule_set_rmd.append('knitr_global_chunk\t' + r'knitr\:\:opts\_chunk\$set\([\"\'](.*)[\"\']\)')
        # rule_set_rmd.append('date\t' + r'\@?date\:\s[\"\'](.*)[\"\']')
        # rule_set_rmd.append('tags\t' + r'\@?tags\:\s[\"\'](.*)[\"\']')
        # rule_set_rmd.append('abstract\t' + r'\@?abstract\:\s[\"\'](.*)[\"\']')
        # rule_set_rmd.append('output\t' + r'\@?output\:\s[\"\'](.*)[\"\']')
        #other parameters
        packlist_crantop100 = 'list_crantop100.txt'
        packlist_geopack = 'list_geopack.txt'
        #process files in target directory
        input_dir = argsdict['input']
        output_modus = argsdict['output']
        extraction_files_directory = argsdict['extractsdir']
        output_to_console = argsdict['outputtostdout']
        for file in os.listdir(input_dir):
            if file.lower().endswith('.r'):
                do_ex(os.path.join(input_dir, file), output_modus, extraction_files_directory, output_to_console, False, rule_set_r)
            if file.lower().endswith('.rmd'):
                do_ex(os.path.join(input_dir, file), output_modus, extraction_files_directory, output_to_console, True, rule_set_rmd_multiline)
        print('done')