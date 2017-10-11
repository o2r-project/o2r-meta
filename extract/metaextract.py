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
###import mimetypes
import os
import re
import sys
import uuid
from subprocess import Popen, PIPE, STDOUT
from xml.dom import minidom

import dicttoxml

###import yaml
from dateutil import parser as dateparser

from helpers.helpers import *
from helpers.http_requests import *

#todo overhaul
def extract_spatial(filepath, fformat):
    try:
        # <side_key> is an dict key in candidates to store all spatial files as list, other than finding the best candidate of spatial file
        side_key = 'global_spatial'
        if side_key not in CANDIDATES_MD_DICT:
            CANDIDATES_MD_DICT[side_key] = {}
        # work on formats:
        coords = None
        if fformat == '.shp':
            # deprecated
            # coords = fiona.open(filepath, 'r')
            return None
        elif fformat == '.json':
            #todo: check if geojson
            return None
        elif fformat == '.geojson':
            #todo: bbox extraction
            return None
        # geojpeg
        elif fformat == '.jp2':
            return None
        # geotif
        elif fformat == '.tif' or fformat == '.tiff':
            return None
        else:
            # all other file extensions: exit
            return None
        # prepare json object:
        new_file_key = {}
        if 'spatial' not in CANDIDATES_MD_DICT[side_key]:
            CANDIDATES_MD_DICT[side_key] = {}
        if 'files' not in CANDIDATES_MD_DICT[side_key]:
            key_files = {'files': []}
            CANDIDATES_MD_DICT[side_key] = key_files
        new_file_key['source_file'] = get_rel_path(filepath)
        new_file_key['geojson'] = {'type': 'Feature',
                                   'geometry': {}
                                }
        if coords is not None:
            new_file_key['geojson']['bbox'] = coords.bounds
            new_file_key['geojson']['geometry']['coordinates'] = [
                [[coords.bounds[0], coords.bounds[1]], [coords.bounds[2], coords.bounds[3]]]]
            new_file_key['geojson']['geometry']['type'] = 'Polygon'
            CANDIDATES_MD_DICT[side_key]['files'].append(new_file_key)
        # calculate union of all available coordinates
        # calculate this only once, at last
        current_coord_list = []
        for key in CANDIDATES_MD_DICT[side_key]['files']:
            if 'geojson' in key:
                if 'geometry' in key['geojson']:
                    if 'coordinates' in key['geojson']['geometry']:
                        if len(key['geojson']['geometry']['coordinates']) > 0:
                            current_coord_list.append((key['geojson']['geometry']['coordinates'][0][0]))
                            current_coord_list.append((key['geojson']['geometry']['coordinates'][0][1]))
        key_union = {}
        coords = calculate_geo_bbox_union(current_coord_list)
        key_union['geojson'] = {}
        if coords is not None:
            key_union['geojson']['bbox'] = [coords[0][0], coords[0][1], coords[1][0], coords[1][1]]
        key_union['geojson']['type'] = 'Feature'
        key_union['geojson']['geometry'] = {}
        key_union['geojson']['geometry']['type'] = 'Polygon'
        if coords is not None:
            key_union['geojson']['geometry']['coordinates'] = coords
        CANDIDATES_MD_DICT[side_key].update({'union': key_union})
    except Exception as exc:
        if dbg:
            raise
        else:
            status_note('! error while parsing spatial information')


def extract_temporal(file_id, filepath, data, timestamp):
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
        if dbg:
            raise
        else:
            status_note('! error while parsing temporal information')


def best_candidate(all_candidates_dict):
    # "all_candidates_dict" contains one dict for each file that was extracted from
    # each features found in each of these dicts is compared here to result in a single dict with max completeness
    global is_debug
    try:
        result = {}
        inputfiles = []
        for key in all_candidates_dict:
            if all_candidates_dict[key] != {}:
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
        return result
    except Exception as exc:
        status_note('! error in candidate management', d=is_debug)
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
        if dbg:
            raise
        else:
            status_note(['! error while creating output: ', exc.args[0]])


def guess_paper_source():
    try:
        # todo: get paperSource from rmd file that has same name as its html rendering
        if 'file' in MASTER_MD_DICT:
            return MASTER_MD_DICT['file']['filename']
        else:
            return None
    except Exception as exc:
        if dbg:
            raise
        else:
            status_note(['! error while guessing paper source: ', exc.args[0]])


def calculate_geo_bbox_union(coordinate_list):
    global is_debug
    try:
        if coordinate_list is None:
            return [(0, 0), (0, 0), (0, 0), (0, 0)]
        min_x = 181.0
        min_y = 181.0
        max_x = -181.0
        max_y = -181.0
        ##max =[181.0, 181.0, -181.0, -181.0]  # proper max has -90/90 & -180/180
        # todo: deal with international date line wrapping / GDAL
        for n in coordinate_list:
            if n[0] < min_x:
                min_x = n[0]
            if n[0] > max_x:
                max_x = n[0]
            if n[1] < min_y:
                min_y = n[1]
            if n[1] > max_y:
                max_y = n[1]
        return [(min_x, min_y), (max_x, min_y), (max_x, max_y), (min_x, max_y)]
    except Exception as exc:
        status_note(['! error while extracting: ', exc.args[0]], d=is_debug)
        raise


def register_parsers():
    global PARSERS_CLASS_LIST
    # todo: generify
    from parsers.parse_bagittxt import ParseBagitTxt
    PARSERS_CLASS_LIST.append(ParseBagitTxt())
    from parsers.parse_geojson import ParseGeojson
    PARSERS_CLASS_LIST.append(ParseGeojson())
    from parsers.parse_rmd import ParseRmd
    PARSERS_CLASS_LIST.append(ParseRmd())
    from parsers.parse_rdata import ParseRData
    PARSERS_CLASS_LIST.append(ParseRData())
    from parsers.parse_yaml import ParseYaml
    PARSERS_CLASS_LIST.append(ParseYaml())
    for x in PARSERS_CLASS_LIST:
            status_note(str(x), d=True)


def get_formats():
    # give out list of supported file formats as provided by importet parser classes
    global PARSERS_CLASS_LIST
    PARSERS_CLASS_LIST = []
    register_parsers()
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
    register_parsers()
    # load rules:
    # rule set for r, compose as: category name TAB entry feature name TAB regex
    global rule_set_r
    # rule_set_r = ['\t'.join(('r_comment', 'comment', r'#{1,3}\s{0,3}([\w\s\:]{1,})')),
    #               #'\t'.join(('Comment', 'seperator', r'#\s?([#*~+-_])\1*')),
    #               '\t'.join(('r_comment', 'codefragment', r'#{1,3}\s*(.*\=.*\(.*\))')),
    #               '\t'.join(('r_comment', 'contact', r'#{1,3}\s*(.*[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.].*)')),
    #               '\t'.join(('r_comment', 'url', r'#{1,3}\s*http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')),
    #               '\t'.join(('depends', '.*installs', r'install.packages\((.*)\)')),
    #               '\t'.join(('depends', '', r'.*library\(\'?\"?([a-zA-Z\d\.]*)[\"\'\)]')),
    #               '\t'.join(('depends', '', r'.*require\(\'?\"?([a-zA-Z\d\.]*)[\"\'\)]')),
    #               '\t'.join(('r_input', 'data input', r'.*data[\(\'\"]{2}([a-zA-Z\d\./\\]*)\"')),
    #               '\t'.join(('r_input', 'data input', r'.*load[\(\'\"]{2}([a-zA-Z\d\./\\]*)\"')),
    #               '\t'.join(('r_input', 'data input', r'.*read[\(\'\"]{2}([a-zA-Z\d\./\\]*)\"')),
    #               '\t'.join(('r_input', 'data input', r'.*read\.csv[\(\'\"]{2}([a-zA-Z\d\./\\]*)\"')),
    #               '\t'.join(('r_input', 'data input', r'.*readGDAL[\(\'\"]{2}([a-zA-Z\d\./\\]*)\"')),
    #               '\t'.join(('r_input', 'data input', r'.*readOGR\(dsn\=[\'\"]{2}([a-zA-Z\d\./\\]*)\"')),
    #               '\t'.join(('r_input', 'data input', r'.*readLines[\(\'\"]{2}([a-zA-Z\d\./\\]*)\"')),
    #               '\t'.join(('r_output', 'file', r'.*write\..*\((.*)\)')),
    #               '\t'.join(('r_output', 'result', r'.*(ggplot|plot|print)\((.*)\)')),
    #               '\t'.join(('r_output', 'setseed', r'.*set\.seed\((.*)\)'))]
    # # rule set for rmd #
    # rule_set_rmd_multiline = ['\t'.join(('yaml', r'---\n(.*?)\n---\n')),
    #                           '\t'.join(('rblock', r'\`{3}(.*)\`{3}'))]
    # other parameters
    global CANDIDATES_MD_DICT
    CANDIDATES_MD_DICT = {}
    global MASTER_MD_DICT  # this one is being updated per function call
    # need this layout for dummy:
    MASTER_MD_DICT = {'author': [],
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
        'viewfiles': [],
        'viewfile': None,
        'version': None}
    bagit_txt_file = None
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
            if os.stat(full_file_path).st_size / 1024 ** 2 > 900:
                continue
            # deal with different input formats:
            file_extension = os.path.splitext(full_file_path)[1].lower()
            status_note(['processing ', os.path.join(root, file).replace('\\', '/')], b=log_buffer)
            # new file / new source
            nr += 1
            # interact with different file formats:
            for x in PARSERS_CLASS_LIST:
                if hasattr(x, 'get_formats'):
                    if file_extension in x.get_formats():
                        if hasattr(x, 'parse'):
                            #extract_from_candidate(new_id, full_file_path, output_format, output_mode, False, rule_set_r)
                            CANDIDATES_MD_DICT[new_id] = x.parse(p=full_file_path, of=output_format, om=output_mode, md=MASTER_MD_DICT, m=True, xo=stay_offline)


            #if file_extension == '.txt':
            #    if file.lower() == 'bagit.txt':
            #        CANDIDATES_MD_DICT[new_id] = {}
            #        CANDIDATES_MD_DICT[new_id][bagit_txt_file] = parse_bagitfile(full_file_path)
            #elif file_extension == '.r':
            #    extract_from_candidate(new_id, full_file_path, output_format, output_mode, False, rule_set_r)
            #    MASTER_MD_DICT['codefiles'].append(get_rel_path(full_file_path))
            #elif file_extension == '.rmd':
            #    extract_from_candidate(new_id, full_file_path, output_format, output_mode, True, rule_set_rmd_multiline)
            #    parse_temporal(new_id, full_file_path, None, None)
            #elif file_extension == '.rdata':
            #    MASTER_MD_DICT['r_rdata'].append({'file': file,
            #                                      'filepath': get_rel_path(full_file_path),
            #                                      'rdata_preview': get_rdata(full_file_path)})
            #elif file_extension == '.html':
            #    MASTER_MD_DICT['viewfiles'].append(get_rel_path(full_file_path))
            #else:
            #    parse_spatial(full_file_path, file_extension)
    status_note([nr, ' files processed'])
    # pool MD and find best most complete set:
    best = best_candidate(CANDIDATES_MD_DICT)
    # we have a candidate best suited for <metadata_raw.json> main output
    # now merge data_dicts, take only keys that are present in "MASTER_MD_DICT":
    ####status_note(str(best), d=True)  ## test
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
    # \ Add viewfiles if mainfile rmd exists
    if 'viewfiles' in MASTER_MD_DICT:
        # find main file name without ext
        if not MASTER_MD_DICT['viewfiles']:
            if 'file' in MASTER_MD_DICT:
                if 'filepath' in MASTER_MD_DICT['file']:
                    if MASTER_MD_DICT['file']['filepath'] is not None:
                        if MASTER_MD_DICT['file']['filepath'].lower().endswith('.rmd'):
                            if os.path.isfile(MASTER_MD_DICT['file']['filepath']):
                                main_file_name, file_extension = os.path.splitext(MASTER_MD_DICT['file']['filepath'])
                                if os.path.isfile(''.join((main_file_name, '.html'))):
                                    MASTER_MD_DICT['viewfiles'].append(''.join((main_file_name, '.html')))
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
