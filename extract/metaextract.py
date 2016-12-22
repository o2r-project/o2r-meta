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
import datetime
import json
import os
import re
import sys
from xml.dom import minidom

import dicttoxml
import orcid
import yaml
from guess_language import guess_language


def find_orcid(txt_input, bln_sandbox):
    try:
        status_note(''.join(('requesting orcid for <', txt_input, '>')))
        api = orcid.SearchAPI(sandbox=bln_sandbox)
        r = api.search_public(txt_input)
        return r['orcid-search-results']['orcid-search-result'][0]['orcid-profile']['orcid-identifier']['path']
    except Exception as exc:
        status_note(''.join(('! warning, could not retrieve orcid for <', txt_input, '>,', exc.args[0])))
        return '0000-0000-0000-0000'
        #return None


def parse_exobj(parameter):
    # to do: get these from live extraction results (o2rexobj.txt)
    # want to know from this function:
    # packages, versions of packages
    # ERCIdentifier
    # uses list(...list(),list(),...) for packages
    result = ''
    return result


def parse_txt_bagitfile(file_path):
    txt_dict = {'bagittxt_file': file_path}
    with open(file_path) as f:
        lines = f.readlines()
        for line in lines:
            s = line.rstrip('\n').split(': ')
            txt_dict[s[0]] = s[1]
    return txt_dict


def parse_yaml(input_text):
    try:
        yaml_data_dict = yaml.safe_load(input_text)
        # get authors and possible ids // orcid
        if yaml_data_dict is not None and not skip_orcid:
            if 'author' in yaml_data_dict:
                if type(yaml_data_dict['author']) is str:
                    id_found = find_orcid(yaml_data_dict['author'], True)
                    yaml_data_dict['orcid'] = id_found
                elif type(yaml_data_dict['author']) is list:
                    for anyone in yaml_data_dict['author']:
                        if 'name' in anyone:
                            # todo: stop using sandbox for orcid retrieval
                            id_found = find_orcid(anyone['name'], True)
                            # status_note('<! debug: '+anyone['name']+' '+id_found+'>')
                            anyone['orcid'] = id_found
        return yaml_data_dict
    except yaml.YAMLError as exc:
        #raise
        status_note(''.join(('! error while parsing yaml input:', str(exc.problem_mark), str(exc.problem))))


def parse_r(input_text):
    try:
        c = 0
        meta_r_dict = {}
        for line in input_text.splitlines():
            c += 1
            for rule in rule_set_r:
                this_rule = rule.split('\t')
                m = re.match(this_rule[2], line)
                if m:
                    if len(m.groups()) > 0:
                        # r comment
                        if this_rule[0] == 'comment':
                            segment = {'feature': this_rule[1], 'line': c, 'text': m.group(1)}
                        # r dependency
                        elif this_rule[0] == 'depends':
                            # get these from live extraction results (o2rexobj.txt)
                            dep_os = parse_exobj('os')
                            dep_packetsys = 'https://cloud.r-project.org/'
                            dep_ver = parse_exobj('version')
                            segment = {'operatingSystem': dep_os,
                                       'packageSystem': dep_packetsys,
                                       'version': dep_ver,
                                       'line': c,
                                       'category': check_rpacks(m.group(1)),
                                       'packageId': m.group(1)}
                        # r other
                        else:
                            segment = {'feature': this_rule[1], 'line': c, 'text': m.group(1)}
                        meta_r_dict.setdefault(this_rule[0], []).append(segment)
        return meta_r_dict
    except Exception as exc:
        #raise
        status_note(''.join(('! error while parsing R input: ', exc.args[0])))


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
def do_ex(path_file, out_format, out_mode, multiline, rule_set):
    try:
        status_note(''.join(('processing ', path_file)))
        md_object_type = ''
        md_interaction_method = ''  # find entry point in ../container/Dockerfile
        md_record_date = datetime.datetime.today().strftime('%Y-%m-%d')
        md_file = os.path.basename(path_file)
        data_dict = {'file': md_file,
                     'filepath': path_file,
                     'ercIdentifier': md_erc_id,
                     'generatedBy': os.path.basename(__file__),
                     'recordDateCreated': md_record_date,
                     'paperSource': md_paper_source,
                     'objectType': md_object_type,
                     'interactionMethod': md_interaction_method}
        with open(os.path.relpath(path_file), encoding='utf-8') as input_file:
            content = input_file.read()
            # apply multiline re for rmd, yaml, etc.
            if multiline:
                # try guess lang
                data_dict['paperLanguage'] = ''
                t = re.search(r'([\w\d\s\.\,\:]{300,1200})', content, flags=re.DOTALL)
                if t:
                    data_dict.update(paperLanguage=guess_language(t.group(1)))
                # process rules
                for rule in rule_set:
                    this_rule = rule.split('\t')
                    s = re.search(this_rule[1], content, flags=re.DOTALL)
                    if s:
                        if this_rule[0].startswith('yaml'):
                            data_dict.update(parse_yaml(s.group(1)))
                        if this_rule[0].startswith('rblock'):
                            data_dict['r_codeblock'] = ''
                            data_dict.update(r_codeblock=parse_r(s.group(1)))
            else:
                # parse entire file as one code block
                data_dict.update(r_codeblock=parse_r(content))
        # save information on this extracted file for comparison with others, so to find best MD
        # ! keep hierarchy:
        # condition: file extension:
        current_ext = os.path.splitext(path_file)[1].lower()
        if 'ext' not in compare_extracted:
            compare_extracted['ext'] = current_ext
            compare_extracted['best'] = data_dict
        else:
            if compare_extracted['ext'] == '.r' and current_ext == '.rmd':
                compare_extracted['ext'] = current_ext
                compare_extracted['best'] = data_dict
            elif compare_extracted['ext'] == '.rmd' and current_ext == '.r':
                pass
            elif compare_extracted['ext'] == '.rmd' and current_ext == '.rmd':
                # already had rmd, and now again rmd, let size decide
                # condition: total size of output:
                current_size = sys.getsizeof(data_dict)
                if 'size' not in compare_extracted:
                    compare_extracted['size'] = current_size
                    compare_extracted['best'] = data_dict
                else:
                    if compare_extracted['size'] < current_size:
                        compare_extracted['size'] = current_size
                        compare_extracted['best'] = data_dict
        # save or output results
        if metafiles_all:
            output_extraction(data_dict, out_format, out_mode, path_file)
    except Exception as exc:
        #raise
        status_note(''.join(('! error while extracting: ', exc.args[0])))


def output_extraction(data_dict, out_format, out_mode, out_path_file):
    try:
        output_data = None
        output_fileext = None
        if out_format == 'json':
            output_data = json.dumps(data_dict, sort_keys=True, indent=4, separators=(',', ': '))
            output_fileext = '.json'
        if out_format == 'xml':
            output_data = minidom.parseString(dicttoxml.dicttoxml(data_dict, attr_type=False)).toprettyxml(indent='\t')
            output_fileext = '.xml'
        if out_mode == '@s':
            # give out to screen
            print(output_data)
            return None
        elif out_mode == '@none':
            # silent mode
            pass
        else:
            # output path is given in <out_mode>
            if out_path_file is not None:
                if os.path.basename(out_path_file) != main_metadata_filename:
                    timestamp = re.sub('\D', '', str(datetime.datetime.now().strftime('%Y%m%d%H:%M:%S.%f')[:-4]))
                    # "meta_" prefix as distinctive feature for metabroker later in workflow
                    out_path_file = os.path.join(out_mode, '_'.join(('meta', timestamp, os.path.basename(out_path_file)[:8].replace('.', '_'), output_fileext)))
            if not os.path.exists(out_mode):
                os.makedirs(out_mode)
            with open(out_path_file, 'w', encoding='utf-8') as outfile:
                outfile.write(output_data)
            status_note(''.join((str(os.stat(out_path_file).st_size), ' bytes written to ', os.path.relpath(out_path_file))))
    except Exception as exc:
        #raise
        status_note(''.join(('! error while ceating output', exc.args[0])))


def status_note(msg):
    print(''.join(('[metaextract] ', str(msg))))


# main:
if __name__ == "__main__":
    if sys.version_info[0] < 3:
        # py2
        status_note('requires py3k or later')
        sys.exit()
    else:
        my_version = 1
        my_mod = ''
        try:
            my_mod = datetime.datetime.fromtimestamp(os.stat(__file__).st_mtime)
        except OSError:
            pass
        status_note(''.join(('v', str(my_version), ' - ', str(my_mod))))
        # args required
        parser = argparse.ArgumentParser(description='args for metaextract')
        parser.add_argument('-i', '--inputdir', help='input directory', required=True)
        group = parser.add_mutually_exclusive_group(required=True)
        group.add_argument('-o', '--outputdir', help='output directory for extraction docs')
        group.add_argument('-s', '--outputtostdout', help='output the result of the extraction to stdout', action='store_true', default=False)
        # args optional
        parser.add_argument('-e', '--ercid', help='erc identifier', required=False)
        parser.add_argument('-xml', '--modexml', help='output xml', action='store_true', default=False, required=False)
        parser.add_argument('-xo', '--skiporcid', help='skip orcid requests', action='store_true', default=False, required=False)
        parser.add_argument('-m', '--metafiles', help='output all metafiles', action='store_true', default=False,  required=False)
        args = parser.parse_args()
        args_dict = vars(args)
        input_dir = args_dict['inputdir']
        md_erc_id = args_dict['ercid']
        skip_orcid = args_dict['skiporcid']
        metafiles_all = args_dict['metafiles']
        # to do: create args for path_to_liveex_logfile and papersource
        output_xml = args_dict['modexml']
        output_dir = args_dict['outputdir']
        output_to_console = args_dict['outputtostdout']
        # output format
        if output_xml:
            output_format = 'xml'
        else:
            output_format = 'json'
        # output mode
        if output_to_console:
            output_mode = '@s'
        elif output_dir:
            output_mode = output_dir
            if not os.path.isdir(output_dir):
                status_note(''.join(('directory <', output_dir, '> will be created during extraction...')))
        else:
            # not possible currently because output arg group is on mutual exclusive
            output_mode = '@none'
        if input_dir:
            if not os.path.isdir(input_dir):
                status_note(''.join(('! error, input dir <', input_dir, '> does not exist')))
                sys.exit()
        # load rules:
        # rule set for r, compose as: category name TAB entry feature name TAB regex
        rule_set_r = ['\t'.join(('comment', 'comment', r'#{1,3}\s{0,3}([\w\s\:]{1,})')),
                      '\t'.join(('comment', 'codefragment', r'#{1,3}\s*(.*\=.*\(.*\))')),
                      '\t'.join(('comment', 'contact', r'#{1,3}\s*(.*[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.].*)')),
                      '\t'.join(('comment', 'url', r'#{1,3}\s*http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')),
                      '\t'.join(('depends', 'installs', r'install.packages\((.*)\)')),
                      '\t'.join(('depends', '', r'library\(\'?\"?([a-zA-Z\d\.]*)[\"\'\)]')),
                      '\t'.join(('depends', '', r'require\(\'?\"?([a-zA-Z\d\.]*)[\"\'\)]')),
                      '\t'.join(('input', 'dataset', r'data\..*\((.*)\)')),
                      '\t'.join(('output', 'file', r'write\..*\((.*)\)')),
                      '\t'.join(('output', 'result', r'(ggplot|plot|print)\((.*)\)')),
                      '\t'.join(('output', 'setseed', r'set\.seed\((.*)\)'))]
        #rule_set_r.append('\t'.join(('Comment', 'seperator', r'#\s?([#*~+-_])\1*')))
        # rule set for rmd #
        rule_set_rmd_multiline = ['\t'.join(('yaml', r'---\n(.*?)\n---\n')),
                                  '\t'.join(('rblock', r'\`{3}(.*)\`{3}'))]
        # other parameters
        packlist_crantop100 = 'list_crantop100.txt'
        packlist_geosci = 'list_geosci.txt'
        nr = 0  # number of files processed
        if skip_orcid:
            status_note('orcid api search disabled...')
        md_paper_source = ''
        bagit_txt_file = None
        compare_extracted = {}  # dict for evaluations to find best metafile for main output
        main_metadata = ''  # main output
        main_metadata_filename = 'metadata.json'
        # process all files in input directory +recursive
        for root, subdirs, files in os.walk(input_dir):
            for file in files:
                if file.lower().endswith('.r'):
                    do_ex(os.path.join(root, file), output_format, output_mode, False, rule_set_r)
                    nr += 1
                elif file.lower() == 'bagit.txt':
                    status_note(''.join(('processing ', os.path.join(root, file))))
                    bagit_txt_file = (parse_txt_bagitfile(os.path.join(root, file)))
                    nr += 1
                elif file.lower().endswith('.rmd'):
                    do_ex(os.path.join(root, file), output_format, output_mode, True, rule_set_rmd_multiline)
                    nr += 1
                else:
                    pass
        status_note(''.join((str(nr), ' files processed ')))
        if 'best' in compare_extracted:
            # we have a candidate best suited for metadata.json main output
            if bagit_txt_file is not None:
                # add data from bagit metafile
                compare_extracted['best']['bagit'] = bagit_txt_file
            if output_mode == '@s' or output_dir is None:
                # write to screen
                output_extraction(compare_extracted['best'], output_format, output_mode, None)
            else:
                # write to file
                output_extraction(compare_extracted['best'], output_format, output_mode, os.path.join(output_dir, main_metadata_filename))
