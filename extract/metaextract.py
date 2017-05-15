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

import datetime
import json
import mimetypes
import os
import re
import sys
import urllib.request
import uuid
from xml.dom import minidom

import dicttoxml
import fiona
import requests
import yaml
from dateutil import parser as dateparser
from guess_language import guess_language


def get_ercspec_http(spec_output_dir):
    if stay_offline:
        status_note('skipping erc spec download (http disabled)')
        return None
    else:
        try:
            spec_url = 'https://github.com/o2r-project/erc-spec/archive/master.zip'  # update
            spec_file = os.path.join(spec_output_dir, 'erc_spec.zip')
            status_note('downloading current erc spec')
            headers = {'User-Agent': 'o2rmeta'}
            req = urllib.request.Request(spec_url, None, headers)
            http = urllib.request.urlopen(req).read()
            with open(spec_file, 'wb') as f:
                f.write(http)
            status_note(''.join(('saved <', spec_file, '>')))
        except:
            status_note('! failed to include download and include spec')


def get_doi_http(md_title, md_author):
    if stay_offline:
        status_note('skipping doi lookup (http disabled)')
        return None
    else:
        try:
            # via Crossref.org
            status_note('requesting doi via crossref.org ...')
            my_params = {'query.title': md_title, 'query.author': md_author}
            r = requests.get('https://api.crossref.org/works', params=my_params, timeout=20)
            #status_note('debug: <get_doi_http> GET ' + r.url)
            status_note(' '.join((str(r.status_code), r.reason)))
            if 'message' in r.json():
                if 'items' in r.json()['message']:
                    if type(r.json()['message']['items']) is list:
                        # take first hit, best match
                        if 'DOI' in r.json()['message']['items'][0]:
                            return r.json()['message']['items'][0]['DOI']
        except requests.exceptions.Timeout:
            status_note('http doi request: timeout')
        except requests.exceptions.TooManyRedirects:
            status_note('http doi request: too many redirects')
        except requests.exceptions.RequestException as e:
            status_note('http doi request: ' + str(e))


def get_orcid_http(txt_input, bln_sandbox):
    if stay_offline:
        status_note('skipping orcid lookup (http disabled)')
        return None
    else:
        try:
            status_note(''.join(('requesting orcid for <', txt_input, '>')))
            headers = {"Content-Type": "application/json"}
            my_params = {"q": txt_input}
            if bln_sandbox:
                r = requests.get('https://pub.sandbox.orcid.org/v2.0/search', params=my_params, headers=headers, timeout=20)
            else:
                r = requests.get('https://pub.orcid.org/v2.0/search', params=my_params, headers=headers, timeout=20)
            status_note(' '.join((str(r.status_code), r.reason)))
            if 'num-found' in r.json():
                if r.json()['num-found'] > 0:
                    if 'result' in r.json():
                        if type(r.json()['result']) is list:
                            if 'orcid-identifier' in r.json()['result'][0]:
                                if 'path' in r.json()['result'][0]['orcid-identifier']:
                                    return str(r.json()['result'][0]['orcid-identifier']['path'])
        except requests.exceptions.Timeout:
            status_note('http orcid request: timeout')
        except requests.exceptions.TooManyRedirects:
            status_note('http orcid request: too many redirects')
        except requests.exceptions.RequestException as e:
            status_note('http orcid request: ' + str(e))


def get_r_package_class(package):
    try:
        list_crantop100 = ['BH', 'DBI', 'Formula', 'Hmisc', 'MASS', 'Matrix',
                           'MatrixModels', 'NMF', 'R6', 'RColorBrewer', 'RCurl', 'RJSONIO',
                           'Rcpp', 'RcppArmadillo', 'RcppEigen', 'SparseM', 'TH.data', 'XML',
                           'acepack', 'assertthat', 'bitops', 'caTools', 'car', 'chron',
                           'colorspace', 'crayon', 'curl', 'data.table', 'devtools', 'dichromat',
                           'digest', 'doParallel', 'dplyr', 'e1071', 'evaluate', 'foreach',
                           'formatR', 'gdata', 'ggplot2', 'git2r', 'gridBase', 'gridExtra',
                           'gtable', 'gtools', 'highr', 'htmltools', 'httr', 'igraph',
                           'irlba', 'iterators', 'jsonlite', 'knitr', 'labeling', 'latticeExtra',
                           'lazyeval', 'lme4', 'lmtest', 'lubridate', 'magrittr', 'maps',
                           'markdown', 'memoise', 'mgcv', 'mime', 'minqa', 'multcomp',
                           'munsell', 'mvtnorm', 'nlme', 'nloptr', 'nnet', 'openssl',
                           'pbkrtest', 'pkgmaker', 'plotrix', 'plyr', 'praise', 'quantreg',
                           'rJava', 'registry', 'reshape2', 'rgl', 'rmarkdown', 'rngtools',
                           'rstudioapi', 'sandwich', 'scales', 'shiny', 'sp', 'stringi',
                           'stringr', 'testthat', 'tidyr', 'whisker', 'withr', 'xlsx',
                           'xlsxjars', 'xtable', 'yaml', 'zoo']
        list_geoscience = ['bfast', 'biclust', 'CARBayes', 'custer', 'devtools', 'dplyr',
                           'fpc', 'geonames', 'geoR', 'georob', 'geospt', 'ggmap',
                           'ggplot2', 'glmmBUGS', 'gstat', 'igraph', 'INLA', 'knitr',
                           'landsat', 'mapdata', 'maps', 'maptools', 'mapview', 'move',
                           'OpenStreetMap', 'PBSmapping', 'plyr', 'RandomFields', 'raster', 'RColorBrewer',
                           'reshape', 'rgdal', 'RgoogleMaps', 'rJava', 'rmarkdown', 'RPostgreSQL',
                           'RStoolbox', 'scidb', 'SciDBR', 'scidbst', 'SDMtools', 'sgeostat',
                           'Snowball', 'sos4R', 'sp', 'spacetime', 'sparr', 'spate',
                           'spatial', 'spatialCovariance', 'SpatioTemporal', 'spatstat', 'spatsurv', 'stats',
                           'stringr', 'strucchange', 'tm', 'tmap', 'trajectories', 'WordCloud',
                           'zoo']
        label = ''
        if package in list_geoscience:
            label += 'geo sciences,'
        if package in list_crantop100:
            label += 'CRAN Top100,'
        if len(label) < 1:
            label = 'none,'
        return label[:-1]
    except:
        #raise
        status_note(''.join(('! error while classifying r package:', str(exc.problem_mark), str(exc.problem))))


def parse_bagitfile(file_path):
    txt_dict = {'bagittxt_file': file_path}
    with open(file_path) as f:
        lines = f.readlines()
        for line in lines:
            s = line.rstrip('\n').split(': ')
            txt_dict[s[0]] = s[1]
    return txt_dict


def parse_r(input_text, parser_dict):
    try:
        c = 0
        for line in input_text.splitlines():
            c += 1
            for rule in rule_set_r:
                this_rule = rule.split('\t')
                m = re.match(this_rule[2], line)
                if m:
                    if len(m.groups()) > 0:
                        # r dependency
                        if this_rule[0] == 'depends':
                            segment = {'packageSystem': 'https://cloud.r-project.org/',
                                       'version': None,
                                       'category': get_r_package_class(m.group(1)),
                                       'identifier': m.group(1)}
                            parser_dict.setdefault('depends', []).append(segment)
                        elif this_rule[0] == 'r_input':
                            segment = {'feature': this_rule[1], 'line': c, 'text': os.path.basename(str(m.group(1)))}
                            parser_dict.setdefault(this_rule[0], []).append(segment)
                        else:
                            segment = {'feature': this_rule[1], 'line': c, 'text': m.group(1)}
                            parser_dict.setdefault(this_rule[0], []).append(segment)
        return parser_dict
    except Exception as exc:
        raise
        #status_note(''.join(('! error while parsing R input: ', str(exc.args[0]))))


def parse_spatial(file_id, filepath, fformat):
    try:
        CANDIDATES_MD_DICT[file_id] = {}
        # work on formats:
        coords = None
        if fformat == '.shp' or fformat == '.geojson':
            coords = fiona.open(filepath, 'r')
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
        if 'spatial' not in CANDIDATES_MD_DICT[file_id]:
            CANDIDATES_MD_DICT[file_id]['spatial'] = {}
        if 'files' not in CANDIDATES_MD_DICT[file_id]['spatial']:
            key_files = {'files': []}
            CANDIDATES_MD_DICT[file_id]['spatial'] = key_files
        new_file_key['source_file'] = filepath
        new_file_key['geojson'] = {}
        if coords is not None:
            new_file_key['geojson']['bbox'] = coords.bounds
        new_file_key['geojson']['type'] = 'Feature'
        new_file_key['geojson']['geometry'] = {}
        if coords is not None:
            new_file_key['geojson']['geometry']['coordinates'] = [
                [[coords.bounds[0], coords.bounds[1]], [coords.bounds[2], coords.bounds[3]]]]
        new_file_key['geojson']['geometry']['type'] = 'Polygon'
        CANDIDATES_MD_DICT[file_id]['spatial']['files'].append(new_file_key)
        # calculate union of all available coordinates
        # calculate this only once, at last
        current_coord_list = []
        for key in CANDIDATES_MD_DICT[file_id]['spatial']['files']:
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
        CANDIDATES_MD_DICT[file_id]['spatial'].update({'union': key_union})
    except:
        raise


def parse_temporal(file_id, filepath, data, timestamp):
    global date_new
    date_new = None
    try:
        if timestamp is not None:
            try:
                # try parse from string, but input is potentially r code
                date_new = dateparser.parse(timestamp).isoformat()
            except:
                raise
                pass
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
    except:
        raise


def parse_yaml(input_text):
    # This is for R markdown files with yaml headers
    try:
        yaml_data_dict = yaml.safe_load(input_text)
        if yaml_data_dict is not None:
            # model description / abstract:
            if 'description' in yaml_data_dict:
                if yaml_data_dict['description'] is not None:
                    MASTER_MD_DICT['description'] = yaml_data_dict['description']
            else:
                if 'abstract' in yaml_data_dict:
                    MASTER_MD_DICT['description'] = yaml_data_dict['abstract']
            # model author:
            if 'author' in yaml_data_dict:
                if type(yaml_data_dict['author']) is str:
                    id_found = get_orcid_http(yaml_data_dict['author'], True)
                    yaml_data_dict['orcid'] = id_found
                    if 'affiliation' not in yaml_data_dict:
                        # we have author but miss affiliation, so add empty list
                        yaml_data_dict['affiliation'] = ""
                    else:
                        # we have affiliation but not an empty list, so make empty list
                        if yaml_data_dict['affiliation'] is None:
                            yaml_data_dict['affiliation'] = ""
                        else:
                            if type(yaml_data_dict['affiliation']) is list:
                                yaml_data_dict['affiliation'] = yaml_data_dict['affiliation'][0]
                elif type(yaml_data_dict['author']) is list:
                    for anyone in yaml_data_dict['author']:
                        if 'name' in anyone:
                            # todo: stop using sandbox for orcid retrieval
                            id_found = get_orcid_http(anyone['name'], True)
                            anyone['orcid'] = id_found
            # model date:
            if 'date' in yaml_data_dict:
                try:
                    parse_temporal(None, None, CANDIDATES_MD_DICT, yaml_data_dict['date'])
                except Exception as exc:
                    status_note(''.join(('[debug] ! failed to parse temporal <', yaml_data_dict['date'],
                                         '> (', str(exc.args[0]), ')')))
            # model doi:
            this_doi = None
            if 'doi' in yaml_data_dict:
                this_doi = yaml_data_dict['doi']
            if 'DOI' in yaml_data_dict:
                this_doi = yaml_data_dict['DOI']
            # other doi source is http request, and will be done later if title + author name is available
            if this_doi is not None:
                # the author might have used the doi tag but added a doi url instead:
                if this_doi.startswith('http'):
                    MASTER_MD_DICT['identifier']['doi'] = this_doi.split('.org/')[1]
                    MASTER_MD_DICT['identifier']['doiurl'] = this_doi
                else:
                    MASTER_MD_DICT['identifier']['doi'] = this_doi
                    MASTER_MD_DICT['identifier']['doiurl'] = ''.join(('https://doi.org/', this_doi))
            # model keywords:
            if 'keywords' in yaml_data_dict:
                # reduce to plain keyword list if given
                if 'plain' in yaml_data_dict['keywords']:
                    yaml_data_dict['keywords'] = yaml_data_dict['keywords']['plain']
            # model keywords:
            if 'title' in yaml_data_dict:
                # reduce to plain title list if given
                if 'plain' in yaml_data_dict['title']:
                    yaml_data_dict['title'] = yaml_data_dict['title']['plain']
            # model interaction / shiny:
            if 'runtime' in yaml_data_dict:
                if yaml_data_dict['runtime'] == 'shiny' and 'interaction' in MASTER_MD_DICT:
                    MASTER_MD_DICT['interaction']['interactive'] = True
        return yaml_data_dict
    except yaml.YAMLError as exc:
        #raise
        status_note(''.join(('! error while parsing yaml input:', str(exc.problem_mark), str(exc.problem))))


def best_candidate(all_candidates_dict):
    # "all_candidates_dict" contains one dict for each file that was extracted from
    # each features found in each of these dicts is compared here to result in a single dict with max completeness
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
                                                inputfiles.append(filename)
                                                break
        result.update({'inputfiles': inputfiles})
        return result
    except:
        raise

# base extract
def extract_from_candidate(file_id, path_file, out_format, out_mode, multiline, rule_set):
    try:
        md_file = os.path.basename(path_file)
        md_mime_type = mimetypes.guess_type(path_file)
        if md_mime_type[0] is None:
            if md_file.lower().endswith('.r'):
                md_mime_type = 'text/plain'
            if md_file.lower().endswith('.rmd'):
                md_mime_type = 'text/markdown'
        if md_erc_id is not None:
            pattern = ''.join(('(', md_erc_id, '.*)'))
            s = re.search(pattern, path_file)
            if s:
                md_filepath = s.group(1)
        else:
            md_filepath = path_file
        md_record_date = datetime.datetime.today().strftime('%Y-%m-%d')
        data_dict = {'file': {'filename': md_file, 'filepath': md_filepath, 'mimetype': md_mime_type},
                    'ercIdentifier': md_erc_id,
                    'recordDateCreated': md_record_date,
                    'depends': []}
        try:
            with open(path_file, encoding='utf-8') as input_file:
                content = input_file.read()
                if multiline:
                    # reset key; try guess lang:
                    data_dict['paperLanguage'] = []
                    t = re.search(r'([\w\d\s\.\,\:]{300,1200})', content, flags=re.DOTALL)
                    if t:
                        if guess_language(t.group(1)) is not None:
                            data_dict['paperLanguage'].append(guess_language(t.group(1)))
                        else:
                            data_dict['paperLanguage'] = []
                    # process rules
                    for rule in rule_set:
                        this_rule = rule.split('\t')
                        s = re.search(this_rule[1], content, flags=re.DOTALL)
                        if s:
                            if this_rule[0].startswith('yaml'):
                                data_dict.update(parse_yaml(s.group(1)))
                            if this_rule[0].startswith('rblock'):
                                #data_dict['r_codeblock'] = ''
                                ##data_dict.update(r_codeblock=parse_r(s.group(1), data_dict))
                                data_dict = parse_r(s.group(1), data_dict)
                else:
                    # parse entire file as one code block
                    #data_dict.update(r_codeblock=parse_r(content, data_dict))
                    data_dict = parse_r(content, data_dict)
        except UnicodeDecodeError:
            status_note(''.join(('! failed to decode <', md_file, '>')))
        # save to list of extracted md:
        CANDIDATES_MD_DICT[file_id] = data_dict
        # save or output results
        if metafiles_all:
            output_extraction(data_dict, out_format, out_mode, path_file)
    except Exception as exc:
        raise
        #status_note(''.join(('! error while extracting: ', exc.args[0])))


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
            status_note(''.join((str(os.stat(out_path_file).st_size), ' bytes written to ', os.path.relpath(out_path_file).replace('\\', '/'))))
    except Exception as exc:
        raise
        #status_note(''.join(('! error while creating output: ', exc.args[0])))


def guess_paper_source():
    try:
        # todo: get paperSource from rmd file that has same name as its html rendering
        if 'file' in MASTER_MD_DICT:
            return MASTER_MD_DICT['file']['filename']
        else:
            return None
    except:
        raise
        #return None


def calculate_geo_bbox_union(coordinate_list):
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
    except:
        raise


def ercyml_write(out_path):
    try:
        if out_path is not None:
            out_path = os.path.join(out_path, 'erc_raw.yml')
            new_id = str(uuid.uuid4())
            spec_version = 1
            data = {'id': new_id,
                    'spec_version': spec_version,
                    'structure': {},
                    'execution': {},
                    'licenses': {},
                    'extensions': {}
                    }
            with open(out_path, 'w', encoding='utf-8') as outfile:
                yaml.dump(data, outfile, default_flow_style=False)
        status_note(out_path + ' written.')
    except:
        raise


def status_note(msg, **kwargs):
    log_buffer = kwargs.get('b', None)
    if not log_buffer:
        print(''.join(('[o2rmeta][extract] ', str(msg))))


def start(**kwargs):
    global input_dir
    input_dir = kwargs.get('i', None)
    global md_erc_id
    md_erc_id = kwargs.get('e', None)
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
            status_note(''.join(('directory <', output_dir, '> will be created during extraction...')))
    else:
        # not possible if output arg group is on mutual exclusive
        output_mode = '@none'
    if input_dir:
        if not os.path.isdir(input_dir):
            status_note(''.join(('! error, input dir <', input_dir, '> does not exist')))
            sys.exit()
    # load rules:
    # rule set for r, compose as: category name TAB entry feature name TAB regex
    global rule_set_r
    rule_set_r = ['\t'.join(('r_comment', 'comment', r'#{1,3}\s{0,3}([\w\s\:]{1,})')),
                  #'\t'.join(('Comment', 'seperator', r'#\s?([#*~+-_])\1*')),
                  '\t'.join(('r_comment', 'codefragment', r'#{1,3}\s*(.*\=.*\(.*\))')),
                  '\t'.join(('r_comment', 'contact', r'#{1,3}\s*(.*[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.].*)')),
                  '\t'.join(('r_comment', 'url', r'#{1,3}\s*http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')),
                  '\t'.join(('depends', '.*installs', r'install.packages\((.*)\)')),
                  '\t'.join(('depends', '', r'.*library\(\'?\"?([a-zA-Z\d\.]*)[\"\'\)]')),
                  '\t'.join(('depends', '', r'.*require\(\'?\"?([a-zA-Z\d\.]*)[\"\'\)]')),
                  '\t'.join(('r_input', 'data input', r'.*data[\(\'\"]{2}([a-zA-Z\d\./\\]*)\"')),
                  '\t'.join(('r_input', 'data input', r'.*load[\(\'\"]{2}([a-zA-Z\d\./\\]*)\"')),
                  '\t'.join(('r_input', 'data input', r'.*read[\(\'\"]{2}([a-zA-Z\d\./\\]*)\"')),
                  '\t'.join(('r_input', 'data input', r'.*read\.csv[\(\'\"]{2}([a-zA-Z\d\./\\]*)\"')),
                  '\t'.join(('r_input', 'data input', r'.*readGDAL[\(\'\"]{2}([a-zA-Z\d\./\\]*)\"')),
                  '\t'.join(('r_input', 'data input', r'.*readOGR\(dsn\=[\'\"]{2}([a-zA-Z\d\./\\]*)\"')),
                  '\t'.join(('r_input', 'data input', r'.*readLines[\(\'\"]{2}([a-zA-Z\d\./\\]*)\"')),
                  '\t'.join(('r_output', 'file', r'.*write\..*\((.*)\)')),
                  '\t'.join(('r_output', 'result', r'.*(ggplot|plot|print)\((.*)\)')),
                  '\t'.join(('r_output', 'setseed', r'.*set\.seed\((.*)\)'))]
    # rule set for rmd #
    rule_set_rmd_multiline = ['\t'.join(('yaml', r'---\n(.*?)\n---\n')),
                              '\t'.join(('rblock', r'\`{3}(.*)\`{3}'))]
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
        'inputfiles': [],
        'keywords': [],
        'license': 'cc-by',  # default
        'access_right': 'open',  # default
        'paperLanguage': [],
        'paperSource': None,
        'publicationDate': None,
        'publication_type': 'other',  # default
        'r_comment': [],
        'r_input': [],
        'r_output': [],
        'recordDateCreated': None,
        'researchQuestions': [],
        'researchHypotheses': [],
        'softwarePaperCitation': None,
        'spatial': {'files': [], 'union': []},
        'temporal': {'begin': None, 'end': None},
        'title': None,
        'upload_type': 'publication',  # default
        'viewfile': [],
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
    except:
        pass
        #raise
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
                file_list_input_candidates.append(full_file_path)
            if nr < 50:
                # use buffering to prevent performance issues when parsing very large numbers of files
                log_buffer = False
            else:
                if not nr % display_interval:
                    log_buffer = False
                    status_note(''.join((str(nr), ' files processed')), b=log_buffer)
                else:
                    log_buffer = True
            # skip large files, config max file size in mb here
            if os.stat(full_file_path).st_size / 1024 ** 2 > 900:
                continue
            # deal with different input formats:
            file_extension = os.path.splitext(full_file_path)[1].lower()
            status_note(''.join(('processing ', os.path.join(root, file).replace('\\', '/'))), b=log_buffer)
            # new file / new source
            nr += 1
            # interact with different file formats:
            if file_extension == '.txt':
                if file.lower() == 'bagit.txt':
                    CANDIDATES_MD_DICT[new_id] = {}
                    CANDIDATES_MD_DICT[new_id][bagit_txt_file] = (parse_bagitfile(full_file_path))
            elif file_extension == '.r':
                extract_from_candidate(new_id, full_file_path, output_format, output_mode, False, rule_set_r)
            elif file_extension == '.rmd':
                extract_from_candidate(new_id, full_file_path, output_format, output_mode, True, rule_set_rmd_multiline)
                parse_temporal(new_id, full_file_path, None, None)
            elif file_extension == '.html':
                MASTER_MD_DICT['viewfile'].append(full_file_path)
            else:
                parse_spatial(new_id, full_file_path, file_extension)
    status_note(''.join((str(nr), ' files processed')))
    # pool MD and find best most complete set:
    best = best_candidate(CANDIDATES_MD_DICT)
    # we have a candidate best suited for <metadata_raw.json> main output
    # now merge data_dicts, take only keys that are present in "MASTER_MD_DICT":
    for key in best:
        if key in MASTER_MD_DICT:
            MASTER_MD_DICT[key] = best[key]
    # Make final adjustments on the master dict before output:
    # \ Fix and complete author element, if existing:
    if 'author' in MASTER_MD_DICT:
        if type(MASTER_MD_DICT['author']) is str:
            # this means there is only one author from yaml header in best candidate
            new_author_listobject = []
            author_element = {'name': MASTER_MD_DICT['author']}
            if 'orcid' in MASTER_MD_DICT:
                author_element.update({'orcid': MASTER_MD_DICT['orcid']})
                MASTER_MD_DICT.pop('orcid')
            new_author_listobject.append(author_element)
            MASTER_MD_DICT['author'] = new_author_listobject
        if type(MASTER_MD_DICT['author']) is list:
            # fix affiliations
            for author_key in MASTER_MD_DICT['author']:
                if 'affiliation' not in author_key:
                    author_key.update({'affiliation': ''})
    else:
        # 'author' element ist missing, create empty dummy:
        MASTER_MD_DICT['author'] = []
    # \ Try to still get doi, if None but title and author name available
    if MASTER_MD_DICT['identifier']['doi'] is None:
        if MASTER_MD_DICT['title'] is not None and MASTER_MD_DICT['author'][0]['name'] is not None:
            MASTER_MD_DICT['identifier']['doi'] = get_doi_http(MASTER_MD_DICT['title'], MASTER_MD_DICT['author'][0])
            # also add url if get doi was successful
            if MASTER_MD_DICT['identifier']['doi'] is not None:
                MASTER_MD_DICT['identifier']['doiurl'] = ''.join(('https://doi.org/', MASTER_MD_DICT['identifier']['doi']))
    # \ Fix and default publication date if none
    if 'publicationDate' in MASTER_MD_DICT:
        if MASTER_MD_DICT['publicationDate'] is None:
            MASTER_MD_DICT['publicationDate'] = datetime.datetime.today().strftime('%Y-%m-%d')
    # \ add viewfile if mainfile rmd exists
    if 'viewfile' in MASTER_MD_DICT:
        # find main file name without ext
        if MASTER_MD_DICT['viewfile'] is None:
            if 'file' in MASTER_MD_DICT:
                if 'filepath' in MASTER_MD_DICT['file']:
                    if MASTER_MD_DICT['file']['filepath'].lower().endswith('.rmd'):
                        if os.path.isfile(MASTER_MD_DICT['file']['filepath']):
                            main_file_name, file_extension = os.path.splitext(MASTER_MD_DICT['file']['filepath'])
                            if os.path.isfile(''.join((main_file_name, '.html'))):
                                MASTER_MD_DICT['viewfile'].append(''.join((main_file_name, '.html')))
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
        get_ercspec_http(output_dir)
    # Write erc.yml according to ERC spec:
    ercyml_write(output_dir)
