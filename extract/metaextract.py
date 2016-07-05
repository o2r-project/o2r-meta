import argparse
import json
import os
import re
import sys
import xml.etree.cElementTree as elt
from datetime import date
from xml.dom import minidom

def check_rpacks(package):
    if package in open(packlist_crantop100).read():
        return 'CRAN-top100'
    if package in open(packlist_geopack).read():
        return 'geo'
    else:
        return 'none'

#extract
def do_ex(my_pathfile, modus, rule_set):
    c = 0
    output_text = None
    output_fileext = None
    #modus json
    if modus == 'json':
        data_dict = {'file': my_pathfile, 'generator': 'metaextract.py'}
        with open(os.path.relpath(my_pathfile), encoding='utf-8') as inpfile:
            for line in inpfile:
                c += 1
                for rule in rule_set:
                    this_rule = rule.split('\t')
                    m = re.match(this_rule[1], line)
                    if m is not None:
                        if this_rule[0].startswith('dependent'):
                            that_line = {'line': str(c), 'guess': check_rpacks(m.group(1)), 'text': '{}'.format(m.group(1))}
                            data_dict.setdefault(this_rule[0], []).append(that_line)
                        else:
                            that_line = {'line': str(c), 'text': '{}'.format(m.group(1))}
                            data_dict.setdefault(this_rule[0], []).append(that_line)
        #save json
        output_text = json.dumps(data_dict, sort_keys=True, indent=4, separators=(',', ': '))
        output_fileext = ".json"
    #modus xml
    if modus == 'xml':
        root = elt.Element('extracted')
        elt.SubElement(root, 'file').text = str(my_pathfile)
        elt.SubElement(root, 'generator').text = 'metaextract.py'
        with open(os.path.relpath(my_pathfile), encoding='utf-8') as inpfile:
            for line in inpfile:
                c += 1
                for rule in rule_set:
                    this_rule = rule.split('\t')
                    m = re.match(this_rule[1], line)
                    if m is not None:
                        if this_rule[0].startswith('dependent'):
                            elt.SubElement(root, this_rule[0], guess=check_rpacks(m.group(1)), line=str(c)).text = '{}'.format(m.group(1))
                        else:
                            elt.SubElement(root, this_rule[0], line=str(c)).text = '{}'.format(m.group(1))
        #save xml
        output_text = minidom.parseString(elt.tostring(root)).toprettyxml(indent='\t')
        output_fileext = ".xml"
    #write output file
    output_filename = 'metaex_' + os.path.basename(my_pathfile)[:8].replace('.', '_') + '_' + str(date.today()) + output_fileext
    with open(output_filename, 'w', encoding='utf-8') as outfile:
        outfile.write(output_text)
    print(str(os.stat(output_filename).st_size) + ' bytes written to ' + str(output_filename))

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
        packlist_crantop100 = 'list_crantop100.txt'
        packlist_geopack = 'list_geopack.txt'
        #process files in target directory
        input_dir = argsdict['input']
        output_modus = argsdict['output']
        for file in os.listdir(input_dir):
            if file.lower().endswith('.r'):
                do_ex(str(os.path.join(input_dir, file)), output_modus, rule_set_r)
            if file.lower().endswith('.rmd'):
                do_ex(str(os.path.join(input_dir, file)), output_modus, rule_set_rmd)
        print('done')