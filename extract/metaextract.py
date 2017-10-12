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

import datetime
import json
import os
import re
import sys
import uuid
from subprocess import Popen, PIPE, STDOUT
from xml.dom import minidom

import dicttoxml
from dateutil import parser as dateparser
from helpers.helpers import *
from helpers.http_requests import *



def extract_temporal(file_id, filepath, data, timestamp):
    global is_debug
    global date_new
    date_new = None
    try:
        if timestamp is not None:
            try:
                # try parse from string, but input is potentially r code
                date_new = dateparser.parse(timestamp).isoformat()
            except Exception as exc:
                if dbg:
                    raise
                else:
                    status_note('! error while parsing date')
        else:
            if filepath is not None:
                date_new = str(datetime.datetime.fromtimestamp(os.stat(filepath).st_mtime).isoformat())
        if data is not None:
            if 'temporal' in data and date_new is not None:
                if 'begin' in data['temporal'] and 'end' in data['temporal']:
                    date_earliest = data['temporal']['begin']
                    if date_earliest is not None:
                        if date_new < date_earliest:
                            # new candidate is earlier than earliest
                            data['temporal'].update({'begin': date_new})
                    else:
                        # nothing yet, so take this one
                        data['temporal'].update({'begin': date_new})
                    date_latest = data['temporal']['end']
                    if date_latest is not None:
                        if date_new > date_latest:
                            # new candidate is later than latest
                            data['temporal'].update({'end': date_new})
                    else:
                        # nothing yet, so take this one
                        data['temporal'].update({'end': date_new})
    except Exception as exc:
        status_note(str(exc), d=is_debug)


def best_candidate(all_candidates_dict):
    # "all_candidates_dict" contains one dict for each file that was extracted from
    # each feature found in each of these dicts is compared here to result in a single dict with max completeness
    global is_debug
    if all_candidates_dict is None:
        status_note('unable to evaluate best md candidate', d=is_debug)
        return None
    print(str(all_candidates_dict))
    try:
        # first find most complext candidate for 'mainfile' suggestion:
        k_max = 0
        k_max_filename = ''
        for k in all_candidates_dict:
            if k is None:
                continue
            if all_candidates_dict[k] is None:
                continue
            candidate = len(all_candidates_dict[k])
            if candidate > k_max:
                k_max = candidate
                if 'mainfile' in all_candidates_dict[k]:
                    if all_candidates_dict[k]['mainfile'] is not None:
                        k_max_filename = all_candidates_dict[k]['mainfile']
                        print(str(k_max_filename))
        # - - - - - - - - - - - - - - - - -
        # now create compositional dict for all features available
        result = {}
        inputfiles = []
        for key in all_candidates_dict:
            if all_candidates_dict[key] is not None:
                for subkey in all_candidates_dict[key]:
                    # determine completeness
                    if subkey not in result:
                        new_key = {subkey: all_candidates_dict[key][subkey]}
                        result.update(new_key)
                        # include function input file paths
                        if subkey == 'r_input':
                            for inputkey in all_candidates_dict[key][subkey]:
                                if 'text' in inputkey:
                                    for filename in file_list_input_candidates:
                                        # check if r inputfile is among encountered files
                                        if inputkey['text'] == os.path.basename(filename) and inputkey['text'] not in inputfiles:
                                            # keep list entries unique:
                                            if filename not in inputfiles:
                                                inputfiles.append(filename)
                                                break
                    else:
                        # this feature is already present, extracted from another file:
                        # take better version
                        if len(str(result[subkey])) < len(str(all_candidates_dict[key][subkey])):
                            # present key is less complex than new key, hence take new one
                            result.pop(subkey)
                            new_key = {subkey: all_candidates_dict[key][subkey]}
                            result.update(new_key)
                            # include function input file paths
                            if subkey == 'r_input':
                                for inputkey in all_candidates_dict[key][subkey]:
                                    if 'text' in inputkey:
                                        for filename in file_list_input_candidates:
                                            if inputkey['text'] == os.path.basename(filename) and inputkey['text'] not in inputfiles:
                                                if filename not in inputfiles:
                                                    inputfiles.append(filename)
                                                    break
        result.update({'inputfiles': inputfiles})
        result.update({'mainfile': k_max_filename})
        return result
    except Exception as exc:
        status_note(str(exc), d=is_debug)


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
            status_note([str(os.stat(out_path_file).st_size), ' bytes written to ', os.path.relpath(out_path_file).replace('\\', '/')])
    except Exception as exc:
        status_note(str(exc), d=is_debug)


def guess_paper_source():
    try:
        # todo: get paperSource from rmd file that has same name as its html rendering
        if 'file' in MASTER_MD_DICT:
            return MASTER_MD_DICT['file']['filename']
        else:
            return None
    except Exception as exc:
        status_note(str(exc), d=is_debug)





def register_parsers(**kwargs):
    dbg = kwargs.get('dbg', None)
    global PARSERS_CLASS_LIST
    # todo: generify, autoimport from dir /parsers
    from parsers.parse_bagittxt import ParseBagitTxt
    PARSERS_CLASS_LIST.append(ParseBagitTxt())
    from parsers.parse_displayfiles import ParseDisplayFiles
    PARSERS_CLASS_LIST.append(ParseDisplayFiles())
    from parsers.parse_geojson import ParseGeojson
    PARSERS_CLASS_LIST.append(ParseGeojson())
    from parsers.parse_rmd import ParseRmd
    PARSERS_CLASS_LIST.append(ParseRmd())
    from parsers.parse_rdata import ParseRData
    PARSERS_CLASS_LIST.append(ParseRData())
    from parsers.parse_yaml import ParseYaml
    PARSERS_CLASS_LIST.append(ParseYaml())
    if dbg:
        for x in PARSERS_CLASS_LIST:
            status_note(str(x), d=True)


def get_formats(**kwargs):
    dbg = kwargs.get('dbg', None)
    # give out list of supported file formats as provided by importet parser classes
    global PARSERS_CLASS_LIST
    PARSERS_CLASS_LIST = []
    register_parsers(dbg=dbg)
    try:
        formatslist = []
        for cl in PARSERS_CLASS_LIST:
            #status_note(str(type(cl)), d=True)
            for f in cl.get_formats():
                formatslist.append(f)
        status_note('returning list of supported formats:')
        for ff in set(formatslist):
            print(str(ff))
    except Exception as exc:
        status_note(['! error while retrieving supported formats', exc])
        raise


def start(**kwargs):
    global is_debug
    is_debug = kwargs.get('dbg', None)
    global input_dir
    input_dir = kwargs.get('i', None)
    global md_erc_id
    md_erc_id = kwargs.get('e', None)
    global basedir
    basedir = kwargs.get('b', None)
    global stay_offline
    stay_offline = kwargs.get('xo', None)
    global metafiles_all
    metafiles_all = kwargs.get('m', None)
    output_xml = kwargs.get('xml', None)
    output_dir = kwargs.get('o', None)
    output_to_console = kwargs.get('s', None)
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
            status_note(['directory <', output_dir, '> will be created during extraction...'])
    else:
        # not possible if output arg group is on mutual exclusive
        output_mode = '@none'
    if input_dir:
        if not os.path.isdir(input_dir):
            status_note(['! error, input dir <', input_dir, '> does not exist'])
            sys.exit(0)
    # parsers:
    global PARSERS_CLASS_LIST
    PARSERS_CLASS_LIST = []
    register_parsers(dbg=is_debug)
    # other parameters
    global CANDIDATES_MD_DICT
    CANDIDATES_MD_DICT = {}
    global MASTER_MD_DICT  # this one is being updated per function call
    # need this layout for dummy:
    MASTER_MD_DICT = {'author': [],
        'bagit': {'bagittxt_files': []},
        'communities': [{'identifier': 'o2r'}],
        'depends': [],
        'description': None,
        'ercIdentifier': None,
        'file': {'filename': None, 'filepath': None, 'mimetype': None},
        'generatedBy': ' '.join(('o2r-meta', os.path.basename(__file__))),
        'identifier': {'doi': None, 'doiurl': None, 'reserveddoi': None},
        'interaction': {'interactive': False,
            'ui_binding': {'purpose': None,
                'widget': None,
                'code': {'filename': None,
                    'function': None,
                    'shinyInputFunction': None,
                    'shinyRenderFunction': None,
                    'functionParameter': None
                    },
               'variable': None
               }
        },
        'codefiles': [],
        'inputfiles': [],
        'keywords': [],
        'license': {'text': None,
                    'data': None,
                    'code': None,
                    'uibindings': None,
                    'md': None
                    },
        'access_right': 'open',  # default
        'paperLanguage': [],
        'paperSource': None,
        'provenance': [],
        'publicationDate': None,
        'publication_type': 'other',  # default
        'r_comment': [],
        'r_input': [],
        'r_output': [],
        'r_rdata': [],
        'recordDateCreated': None,
        'researchQuestions': [],
        'researchHypotheses': [],
        'softwarePaperCitation': None,
        'spatial': {'files': None, 'union': None},
        'temporal': {'begin': None, 'end': None},
        'title': None,
        'upload_type': 'publication',  # default
        'displayfile': None,
        'displayfile_candidates': [],
        'mainfile': None,
        'mainfile_candidates': [],
        'version': None}
    global compare_extracted
    compare_extracted = {}  # dict for evaluations to find best metafile for main output
    global main_metadata_filename
    main_metadata_filename = 'metadata_raw.json'
    global file_list_input_candidates
    # create dummy file to indicate latest data structure
    try:
        with open(os.path.join("schema", "json", "dummy.json"), 'w', encoding='utf-8') as dummyfile:
            dummyfile.write(json.dumps(MASTER_MD_DICT, sort_keys=True, indent=4, separators=(',', ': ')))
    except Exception as exc:
        if is_debug:
            raise
        else:
            status_note(['! error while extracting: ', exc.args[0]], d=is_debug)
    # process all files in input directory +recursive
    file_list_input_candidates = []  # all files encountered, possible input of an R script
    log_buffer = False
    nr = 0  # number of files processed
    display_interval = 2500  # display progress every X processed files
    for root, subdirs, files in os.walk(input_dir):
        for file in files:
            full_file_path = os.path.join(root, file).replace('\\', '/')
            # give it a number
            new_id = str(uuid.uuid4())
            if os.path.isfile(full_file_path) and full_file_path not in file_list_input_candidates:
                file_list_input_candidates.append(get_rel_path(full_file_path, basedir))
            if nr < 50:
                # use buffering to prevent performance issues when parsing very large numbers of files
                log_buffer = False
            else:
                if not nr % display_interval:
                    log_buffer = False
                    status_note([nr, ' files processed'], b=log_buffer)
                else:
                    log_buffer = True
            # skip large files, config max file size in mb here
            if os.stat(full_file_path).st_size / 1024 ** 2 > 2047:
                status_note(['skipping ', os.path.normpath(os.path.join(root, file)), ' (exceeds max file size)'], b=log_buffer, d=is_debug)
                continue
            # deal with different input formats:
            file_extension = os.path.splitext(full_file_path)[1].lower()
            status_note(['processing ', os.path.normpath(os.path.join(root, file))], b=log_buffer, d=is_debug)
            # new file / new source
            nr += 1
            # interact with different file formats:
            for x in PARSERS_CLASS_LIST:
                if hasattr(x, 'get_formats'):
                    if file_extension in x.get_formats():
                        if hasattr(x, 'parse'):
                            #extract_from_candidate(new_id, full_file_path, output_format, output_mode, False, rule_set_r)
                            CANDIDATES_MD_DICT[new_id] = x.parse(p=full_file_path, ext=file_extension, of=output_format, om=output_mode, md=MASTER_MD_DICT, m=True, xo=stay_offline)
    status_note([nr, ' files processed'])
    # pool MD and find best most complete set:
    best = best_candidate(CANDIDATES_MD_DICT)
    # we have a candidate best suited for <metadata_raw.json> main output
    # now merge data_dicts, take only keys that are present in "MASTER_MD_DICT":
    for key in best:
        #if key == 'author':
        #    continue
        if key in MASTER_MD_DICT:
            MASTER_MD_DICT[key] = best[key]
    # Make final adjustments on the master dict before output:
    # \ Add spatial from candidates:
    if 'spatial' in MASTER_MD_DICT and 'global_spatial' in CANDIDATES_MD_DICT:
        MASTER_MD_DICT['spatial'] = CANDIDATES_MD_DICT['global_spatial']
    if MASTER_MD_DICT['identifier']['doi'] is not None:
        MASTER_MD_DICT['identifier']['doiurl'] = ''.join(('https://doi.org/', MASTER_MD_DICT['identifier']['doi']))
    # \ Fix and default publication date if none
    if 'publicationDate' in MASTER_MD_DICT:
        if MASTER_MD_DICT['publicationDate'] is None:
            MASTER_MD_DICT['publicationDate'] = datetime.datetime.today().strftime('%Y-%m-%d')
    # \ Add display file if mainfile rmd exists
    if 'displayfile_candidates' in MASTER_MD_DICT:
        if 'mainfile' in MASTER_MD_DICT:
            if MASTER_MD_DICT['mainfile'] is not None:
                if os.path.isfile(MASTER_MD_DICT['mainfile']):
                    main_pathfile_name, file_extension = os.path.splitext(MASTER_MD_DICT['mainfile'])
                    # check if display file candidate with same name as mainfile but a display file extension exists, add it in displayfile element
                    main_basefile_name = os.path.basename(main_pathfile_name)
                    if 'displayfile_candidates' in MASTER_MD_DICT:
                        match = None
                        for x in MASTER_MD_DICT['displayfile_candidates']:
                            x_main, x_extension = os.path.splitext(os.path.basename(x))
                            if x_main == main_basefile_name:
                                match = x
                    if match is not None:
                        MASTER_MD_DICT['displayfile'] = match
    # \ Fix and complete paperSource element, if existing:
    if 'paperSource' in MASTER_MD_DICT:
        MASTER_MD_DICT['paperSource'] = guess_paper_source()
    # Process output
    if output_mode == '@s' or output_dir is None:
        # write to screen
        output_extraction(MASTER_MD_DICT, output_format, output_mode, None)
    else:
        # write to file
        output_extraction(MASTER_MD_DICT, output_format, output_mode, os.path.join(output_dir, main_metadata_filename))
        get_ercspec_http(output_dir, stay_offline)
