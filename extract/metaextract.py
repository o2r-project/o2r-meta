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
import fiona
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
                                       'category': classify_r_package(m.group(1)),
                                       'packageId': m.group(1)}
                        # r other
                        else:
                            segment = {'feature': this_rule[1], 'line': c, 'text': m.group(1)}
                        meta_r_dict.setdefault(this_rule[0], []).append(segment)
        return meta_r_dict
    except Exception as exc:
        raise
        #status_note(''.join(('! error while parsing R input: ', str(exc.args[0]))))


def classify_r_package(package):
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
        raise


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
            status_note(''.join((str(os.stat(out_path_file).st_size), ' bytes written to ', os.path.relpath(out_path_file))))
    except Exception as exc:
        #raise
        status_note(''.join(('! error while ceating output', exc.args[0])))


def geo_bbox_union(coordinate_list):
    try:
        if coordinate_list is None:
            return [(0, 0), (0, 0), (0, 0), (0, 0)]
        min_x = 181.0  # start with something much higher than expected min
        min_y = 181.0
        max_x = -181.0  # start with something much lower than expected max
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


def parse_geo(filepath, data, fformat):
    try:
        new_file_key = {}
        if 'spatial' not in data:
            data['spatial'] = {}
        if 'files' not in data['spatial']:
            key_files = {}
            key_files['files'] = []
            data['spatial'] = key_files
        # work on formats:
        status_note('processing ' + filepath)
        coords = None
        if fformat == 'shp' or fformat == 'geojson':
            coords = fiona.open(filepath, 'r')
        elif fformat == 'geotiff':
            return None
            #pass
        else:
            pass
        new_file_key['source_file'] = filepath
        new_file_key['geojson'] = {}
        if coords is not None:
            new_file_key['geojson']['bbox'] = coords.bounds
        new_file_key['geojson']['bbox'] = ''
        new_file_key['geojson']['type'] = 'Feature'
        new_file_key['geojson']['geometry'] = {}
        if coords is not None:
            new_file_key['geojson']['geometry']['coordinates'] = [
                [[coords.bounds[0], coords.bounds[1]], [coords.bounds[2], coords.bounds[3]]]]
        new_file_key['geojson']['geometry']['type'] = 'Polygon'
        data['spatial']['files'].append(new_file_key)
        # calculate union of all available coordinates
        # calculate this only once, at last
        current_coord_list = []
        for key in data['spatial']['files']:
            if 'geojson' in key:
                if 'geometry' in key['geojson']:
                    if 'coordinates' in key['geojson']['geometry']:
                        if len(key['geojson']['geometry']['coordinates']) > 0:
                            current_coord_list.append((key['geojson']['geometry']['coordinates'][0][0]))
                            current_coord_list.append((key['geojson']['geometry']['coordinates'][0][1]))
        key_union = {}
        key_union['geojson'] = {}
        #key_union['geojson']['bbox'] = [0,0,0,0] # bbox of geo_bbox_union(current_coord_list) in geojson format
        key_union['geojson']['type'] = 'Feature'
        key_union['geojson']['geometry'] = {}
        key_union['geojson']['geometry']['type'] = 'Polygon'
        key_union['geojson']['geometry']['coordinates'] = geo_bbox_union(current_coord_list)
        data['spatial'].update({'union': key_union})
    except:
        raise


def status_note(msg):
    print(''.join(('[o2rmeta][extract] ', str(msg))))


def start(**kwargs):
    input_dir = kwargs.get('i', None)
    global md_erc_id
    md_erc_id = kwargs.get('e', None)
    global skip_orcid
    skip_orcid = kwargs.get('xo', None)
    global metafiles_all
    metafiles_all = kwargs.get('m', None)
    # to do: create args for path_to_liveex_logfile and papersource
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
    nr = 0  # number of files processed
    if skip_orcid:
        status_note('orcid api search disabled...')
    global md_paper_source
    md_paper_source = ''
    global MASTER_MD_DICT
    MASTER_MD_DICT = {}  # this one is being updated per function call
    bagit_txt_file = None
    global compare_extracted
    compare_extracted = {}  # dict for evaluations to find best metafile for main output
    global main_metadata_filename
    main_metadata_filename = 'metadata_raw.json'
    # process all files in input directory +recursive
    for root, subdirs, files in os.walk(input_dir):
        #status_note(''.join(('debug: encountering ', str(list(files)))))
        for file in files:
            if file.lower().endswith('.r'):
                do_ex(os.path.join(root, file), output_format, output_mode, False, rule_set_r)
                nr += 1
            elif file.lower() == 'bagit.txt':
                status_note(''.join(('processing ', os.path.join(root, file).replace('\\', '/'))))
                MASTER_MD_DICT[bagit_txt_file] = (parse_txt_bagitfile(os.path.join(root, file).replace('\\', '/')))
                nr += 1
            elif file.lower().endswith('.rmd'):
                do_ex(os.path.join(root, file).replace('\\', '/'), output_format, output_mode, True, rule_set_rmd_multiline)
                nr += 1
            elif file.lower().endswith('.shp'):
                parse_geo(os.path.join(root, file).replace('\\', '/'), MASTER_MD_DICT, 'shp')
                nr += 1
            elif file.lower().endswith('.geojson'):
                # todo: check .json for geojson-ness
                parse_geo(os.path.join(root, file).replace('\\', '/'), MASTER_MD_DICT, 'geojson')
                nr += 1
            elif file.lower().endswith('.tif'):
                # todo: check .json for geojson-ness
                parse_geo(os.path.join(root, file).replace('\\', '/'), MASTER_MD_DICT, 'geotiff')
                nr += 1
            else:
                pass
    status_note(''.join((str(nr), ' files processed ')))
    if 'best' in compare_extracted:
        # we have a candidate best suited for <metadata_raw.json> main output
        # now merge data_dicts:
        for key in compare_extracted['best']:
            MASTER_MD_DICT[key] = compare_extracted['best'][key]
        if output_mode == '@s' or output_dir is None:
            # write to screen
            output_extraction(MASTER_MD_DICT, output_format, output_mode, None)
        else:
            # write to file
            output_extraction(MASTER_MD_DICT, output_format, output_mode, os.path.join(output_dir, main_metadata_filename))
