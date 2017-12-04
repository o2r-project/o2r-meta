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
from xml.dom import minidom

import dicttoxml

from helpers.helpers import *
from helpers.http_requests import *


def best_candidate(all_candidates_dict):
    # "all_candidates_dict" contains one dict for each file that was extracted from
    # each feature found in each of these dicts is compared here to result in a single dict with max completeness
    global is_debug
    if all_candidates_dict is None:
        status_note('unable to evaluate best md candidate', d=is_debug)
        return None
    else:
        if all_candidates_dict == {}:
            return None
        else:
            abort = True
            # test all entries empty and abort if no content:
            for none_test in all_candidates_dict:
                if all_candidates_dict[none_test] is not None:
                    abort = False
            if abort:
                return None
            else:
                try:
                    # first find most complex candidate for 'mainfile' suggestion:
                    k_max = 0
                    k_max_filename = ''
                    for k in all_candidates_dict:
                        if k is None:
                            continue
                        if all_candidates_dict[k] is None:
                            continue
                        candidate = len(all_candidates_dict[k])
                        if candidate > k_max:
                            if 'mainfile' in all_candidates_dict[k]:
                                if all_candidates_dict[k]['mainfile'] is not None:
                                    k_max = candidate
                                    k_max_filename = all_candidates_dict[k]['mainfile']
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
                    #todo: catch if inputdir is deeper than outputdir
                    if basedir is not None:
                        result.update({'mainfile': os.path.normpath(os.path.relpath(k_max_filename, basedir))})
                    else:
                        result.update({'mainfile': os.path.basename(k_max_filename)})
                    return result
                except Exception as exc:
                    status_note(str(exc), d=is_debug)
                    raise


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
                if os.path.basename(out_path_file) != CONFIG['output_md_filename']:
                    timestamp = re.sub('\D', '', str(datetime.datetime.now().strftime('%Y%m%d%H:%M:%S.%f')[:-4]))
                    # "meta_" prefix as distinctive feature for metabroker later in workflow
                    out_path_file = os.path.join(out_mode, '_'.join(('meta', timestamp, os.path.basename(out_path_file)[:8].replace('.', '_'), output_fileext)))
            if not os.path.exists(out_mode):
                os.makedirs(out_mode)
            with open(out_path_file, 'w', encoding='utf-8') as outfile:
                outfile.write(output_data)
            status_note([str(round(os.stat(out_path_file).st_size / 1024, 4)), ' KB written to ', os.path.normpath(os.path.relpath(out_path_file))])
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
    from parsers.parse_netcdf import ParseNetcdf
    PARSERS_CLASS_LIST.append(ParseNetcdf())
    from parsers.parse_ogc_shp import ParseGeopackage
    PARSERS_CLASS_LIST.append(ParseGeopackage())
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
        status_note('returning list of supported formats:', d=False)
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
    global PARSERS_CLASS_LIST
    PARSERS_CLASS_LIST = []
    register_parsers(dbg=is_debug)

    global CONFIG
    # Configure meta extract here:
    CONFIG = {'extract_max_file_size_mb': 2047,
              'display_threshold': 2500,
              'buffer_size_number_of_files': 50,
              'output_md_filename': 'metadata_raw.json'}
    global CANDIDATES_MD_DICT
    CANDIDATES_MD_DICT = {}
    global MASTER_MD_DICT
    MASTER_MD_DICT = {'author': [],
        'bagit': {'bagittxt_files': []},
        'communities': [{'identifier': 'o2r'}],
        'depends': [],
        'description': None,
        'ercIdentifier': md_erc_id,
        'file': {'filename': None, 'filepath': None, 'mimetype': None},
        'generatedBy': ' '.join(('o2r-meta', os.path.basename(__file__))),
        'identifier': {'doi': None, 'doiurl': None, 'reserveddoi': None},
        'interaction': [],  # {'shinyURL': {'path': 'pathToShinyURL', 'type': 'text/shiny'}, 'underlyingdata': '#pathToData', underlyingCode: '#pathToCode'}
        'codefiles': [],
        'inputfiles': [],
        'keywords': [],
        'license': {'text': None,
                    'data': None,
                    'code': None,
                    'uibindings': None,
                    'md': None
                    },
        'ncdf': {'ncdf_files': []},
        'access_right': 'open',
        'paperLanguage': [],
        'provenance': [],
        'publicationDate': None,
        'publication_type': 'other',
        'r_comment': [],
        'r_input': [],
        'r_output': [],
        'r_rdata': [],
        'recordDateCreated': None,
        'researchQuestions': [],
        'researchHypotheses': [],
        'softwarePaperCitation': None,
        'spatial': {'files': [], 'union': None},
        'temporal': {'begin': None, 'end': None},
        'title': None,
        'upload_type': 'publication',
        'displayfile': None,
        'displayfile_candidates': [],
        'mainfile': None,
        'mainfile_candidates': [],
        'version': None}
    global file_list_input_candidates
    # create dummy file if in debug mode to indicate latest data structure
    if is_debug:
        try:
            with open(os.path.join(os.path.dirname(sys.modules['__main__'].__file__), 'schema', 'json', 'dummy.json'), 'w', encoding='utf-8') as f:
                f.write(json.dumps(MASTER_MD_DICT, sort_keys=True, indent=4, separators=(',', ': ')))
        except Exception as exc:
                status_note(['! could not write md dummy file: ', exc.args[0]], d=is_debug)
    # process all files in input directory recursively
    file_list_input_candidates = []  # all files encountered, possible input of an R script
    log_buffer = False
    nr = 0  # number of files processed
    nr_errs = 0  # number of errors occured
    nr_skips = 0  # number of skipped files
    display_interval = CONFIG['display_threshold'] # display progress every X processed files
    for root, subdirs, files in os.walk(input_dir):
        for file in files:
            full_file_path = os.path.join(root, file).replace('\\', '/')
            # give it a number
            new_id = str(uuid.uuid4())
            if os.path.isfile(full_file_path) and full_file_path not in file_list_input_candidates:
                file_list_input_candidates.append(os.path.relpath(full_file_path, basedir))
            if nr < CONFIG['buffer_size_number_of_files']:
                # use buffering to prevent performance issues when parsing very large numbers of files
                log_buffer = False
            else:
                if not nr % display_interval:
                    log_buffer = False
                    status_note([nr, ' files processed'], b=log_buffer)
                else:
                    log_buffer = True
            # skip large files, config max file size in mb here
            if os.stat(full_file_path).st_size / 1024 ** 2 > CONFIG['extract_max_file_size_mb']:
                status_note(['skipping ', os.path.normpath(os.path.join(root, file)), ' (exceeds max file size)'], b=log_buffer, d=is_debug)
                nr_skips += 1
                continue
            # deal with different input formats:
            file_extension = os.path.splitext(full_file_path)[1].lower()
            # interact with different file formats:
            has_been_processed = False
            has_failed = False
            for x in PARSERS_CLASS_LIST:
                if hasattr(x, 'get_formats'):
                    if file_extension in x.get_formats():
                        if hasattr(x, 'parse'):
                            cache_extracted = x.parse(p=full_file_path, ext=file_extension, of=output_format, om=output_mode, md=MASTER_MD_DICT, bd=basedir, m=True, is_debug=is_debug, xo=stay_offline)
                            if cache_extracted == 'error':
                                has_failed = True
                            else:
                                CANDIDATES_MD_DICT[new_id] = cache_extracted
                                has_been_processed = True
            if has_been_processed:
                if has_failed:
                    nr_errs += 1
                    status_note(['failed to extract: ', os.path.normpath(os.path.join(root, file))], b=log_buffer, d=is_debug)
                else:
                    nr += 1
                    status_note(['extracted from: ', os.path.normpath(os.path.join(root, file))], b=log_buffer, d=is_debug)
    status_note(['total files processed: ', nr], d=False)
    status_note(['total extraction errors: ', nr_errs], d=False)
    status_note(['total skipped files: ', nr_skips], d=False)
    # pool MD and find best most complete set:
    best = best_candidate(CANDIDATES_MD_DICT)
    # we have a candidate best suited for <metadata_raw.json> main output
    # now merge data dicts, take only keys that are present in "MASTER_MD_DICT":
    if best is None:
        status_note('Warning: could not find extractable content', d=False)
        output_extraction(MASTER_MD_DICT, output_format, output_mode, os.path.join(output_dir, CONFIG['output_md_filename']))
        sys.exit(0)
    else:
        for key in best:
            #if key == 'author':
            #    continue
            if key in MASTER_MD_DICT:
                MASTER_MD_DICT[key] = best[key]
        # Make final adjustments on the master dict before output:
        # \ Add spatial from candidates:
        if 'spatial' in MASTER_MD_DICT:
            if 'files' in MASTER_MD_DICT['spatial']:
                coorlist = []
                for key in MASTER_MD_DICT['spatial']['files']:
                    if 'bbox' in key:
                        coorlist.append(key['bbox'])
                MASTER_MD_DICT['spatial']['union'] = {'bbox': calculate_geo_bbox_union(coorlist)}
        # Identifier
        if MASTER_MD_DICT['identifier']['doi'] is not None:
            MASTER_MD_DICT['identifier']['doiurl'] = ''.join(('https://doi.org/', MASTER_MD_DICT['identifier']['doi']))
        # \ Fix and default publication date if none
        if 'publicationDate' in MASTER_MD_DICT:
            if MASTER_MD_DICT['publicationDate'] is None:
                MASTER_MD_DICT['publicationDate'] = datetime.datetime.today().strftime('%Y-%m-%d')
        # \ Add display file if mainfile rmd exists
        if 'displayfile_candidates' in MASTER_MD_DICT:
            if 'displayfile' in MASTER_MD_DICT:
                if not MASTER_MD_DICT['displayfile']:
                    # take next best candidate
                    if len(MASTER_MD_DICT['displayfile_candidates']) >= 1:
                        MASTER_MD_DICT['displayfile'] = MASTER_MD_DICT['displayfile_candidates'][0]
                # refine candidate if matching mainfile
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
        # Process output
        if output_mode == '@s' or output_dir is None:
            # write to screen
            output_extraction(MASTER_MD_DICT, output_format, output_mode, None)
        else:
            # write to file
            output_extraction(MASTER_MD_DICT, output_format, output_mode, os.path.join(output_dir, CONFIG['output_md_filename']))
            get_ercspec_http(output_dir, stay_offline)
