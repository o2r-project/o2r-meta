#!/usr/bin/env python
# -*- coding: utf-8 -*-

import mimetypes
import os
import re
import sys
import xml.etree.cElementTree as elt
from datetime import date
from xml.dom import minidom
import argparse


def check_rpacks(package):
    if package in open(packlist_crantop100).read():
        return 'CRAN-top100'
    if package in open(packlist_geopack).read():
        return 'geo'
    else:
        return 'none'

#extract for R
def do_ex(my_pathfile, modus):
    c=0
    root = elt.Element('extracted')
    elt.SubElement(root, 'file').text = str(my_pathfile)
    elt.SubElement(root, 'mime-type').text = str(mimetypes.guess_type(my_pathfile, strict=False)[1]) #include non IANA mimes
    elt.SubElement(root, 'generator', mode=modus).text = 'metaextract.py'
    if modus == 'r':
        with open(os.path.relpath(my_pathfile), encoding='utf-8') as inpfile:
                for line in inpfile:
                    c+=1
                    for rule in rule_set_r:
                        this_rule = rule.split('\t')
                        m = re.match(this_rule[1], line)
                        if m is not None:
                            if this_rule[0].startswith('dependent'):
                                elt.SubElement(root, this_rule[0], guess=check_rpacks(m.group(1)), line=str(c)).text = '{}'.format(m.group(1))
                            else:
                                elt.SubElement(root, this_rule[0], line=str(c)).text = '{}'.format(m.group(1))
    if modus == 'rmd':
        with open(os.path.relpath(my_pathfile), encoding='utf-8') as inpfile:
                for line in inpfile:
                    c+=1
                    for rule in rule_set_rmd:
                        this_rule = rule.split('\t')
                        m = re.match(this_rule[1], line)
                        if m is not None:
                            if this_rule[0].startswith('dependent'):
                                elt.SubElement(root, this_rule[0], guess=check_rpacks(m.group(1)), line=str(c)).text = '{}'.format(m.group(1))
                            else:
                                elt.SubElement(root, this_rule[0], line=str(c)).text = '{}'.format(m.group(1))
    #save
    metae = minidom.parseString(elt.tostring(root)).toprettyxml(indent='\t')
    output_filename = 'metaex_' + os.path.basename(my_pathfile)[:8].replace('.', '_') + '_' + str(date.today()) + '.xml'
    with open(output_filename, 'w', encoding='utf-8') as outfile:
        outfile.write(metae)
    print(str(os.stat(output_filename).st_size) + ' bytes written to ' + str(output_filename))

# Main:
if __name__ == "__main__":
    if sys.version_info[0] < 3:
        #py2
        print('requires py3k or later')
        sys.exit()
    else:
        #py3k
        #args
        parser = argparse.ArgumentParser(description='description')
        parser.add_argument('-i', '--input', help='input dir', required=True)
        parser.add_argument('-o', '--output', help='output format xml or json', required=True)
        args = parser.parse_args()
        argsdict = vars(args)
        print('initializing...')
        #enter rules for r
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
        #enter rules for rmd
        rule_set_rmd = []
        rule_set_rmd.append('author\t' + r'\@?author\:\s\"(.*)\"')
        rule_set_rmd.append('codeblock_start\t' + r'\`\`\`\{(.*)\}')
        rule_set_rmd.append('related_file_knitr\t' + r'knitr\:\:read\_chunk\([\"\'](.*)[\"\']\)')
        rule_set_rmd.append('title\t' + r'\@?title\:\s[\"\'](.*)[\"\']')
        #other parameters
        mimetypes.init(files=None)
        packlist_crantop100 = 'list_crantop100.txt'
        packlist_geopack = 'list_geopack.txt'
        input_dir = argsdict['input']
        if argsdict['output'] == 'json':
            #process files in target directory
            print('output: json to be implemented')
        if argsdict['output'] == 'xml':
            print('output: xml')
            #process files in target directory
            for file in os.listdir(input_dir):
                if file.lower().endswith('.r'):
                    do_ex(str(os.path.join(input_dir, file)), 'r')
                if file.lower().endswith('.rmd'):
                    do_ex(str(os.path.join(input_dir, file)), 'rmd')
            print('done')