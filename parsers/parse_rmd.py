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
__all__ = ['ParseRmd']

import json
import os
import re
import datetime
from guess_language import guess_language
from helpers.helpers import *

ID = 'o2r meta rmd parser'
FORMATS = ['.rmd', '.r']

rule_set_r = ['\t'.join(('r_comment', 'comment', r'#{1,3}\s{0,3}([\w\s\:]{1,})')),
              # '\t'.join(('Comment', 'seperator', r'#\s?([#*~+-_])\1*')),
              '\t'.join(('r_comment', 'codefragment', r'#{1,3}\s*(.*\=.*\(.*\))')),
              '\t'.join(
                  ('r_comment', 'contact', r'#{1,3}\s*(.*[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.].*)')),
              '\t'.join(('r_comment', 'url',
                         r'#{1,3}\s*http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')),
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
              '\t'.join(('r_input', 'data input', r'.*read[r\.\:\_].*file[\s]{0,1}\=[\s]{0,1}[\"\']{0,1}([0-9A-Za-z\,\.\:\/\\]*)[\"\']{1,1}')),
              '\t'.join(('r_input', 'data output', r'.*write.csv\(.*[\,\s]{0,2}[\'\"]{1}([a-zA-Z\d\.]*)[\'\"]{1}\)')),
              '\t'.join(('r_output', 'result', r'.*(ggplot|plot|print)\((.*)\)')),
              '\t'.join(('r_output', 'setseed', r'.*set\.seed\((.*)\)'))]
# rule set for rmd #
rule_set_rmd_multiline = ['\t'.join(('yaml', r'---\n(.*?)\n---\n')),
                          '\t'.join(('rblock', r'\`{3}(.*)\`{3}'))]


class ParseRmd:
    @staticmethod
    def get_id():
        return str(ID)

    @staticmethod
    def get_formats():
        return FORMATS

    def parse(self, **kwargs):
        try:
            path_file = kwargs.get('p', None)
            MASTER_MD_DICT = kwargs.get('md', None)
            multiline = kwargs.get('m', None)
            is_debug = kwargs.get('is_debug', None)
            stay_offline = kwargs.get('xo', None)
            data_dict = {'mainfile': path_file,
                        'depends': []
                         }
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
                        for rule in rule_set_rmd_multiline:
                            this_rule = rule.split('\t')
                            s = re.search(this_rule[1], content, flags=re.DOTALL)
                            if s:
                                if this_rule[0].startswith('yaml'):
                                    from parsers.parse_yaml import ParseYaml
                                    parsed = ParseYaml().internal_parse(s.group(1), MASTER_MD_DICT, stay_offline, is_debug)
                                    if parsed == 'error':
                                        return parsed
                                    else:
                                        data_dict.update(parsed)
                                if this_rule[0].startswith('rblock'):
                                    data_dict = parse_r(s.group(1), data_dict)
                    else:
                        # parse entire file as one code block
                        data_dict.update(r_codeblock=parse_r(content, data_dict))
            except UnicodeDecodeError:
                status_note(['! error, failed to decode <', md_file, '>'], d=is_debug)
                return 'error'
            # save to list of extracted metadata:
            data_dict['provenance'] = get_prov(path_file)
            return data_dict
            # save or output results
            # todo: reenable that option:
            #if metafiles_all:
            #    output_extraction(data_dict, out_format, out_mode, path_file)
        except Exception as exc:
            status_note('! error while extracting Rmd', d=is_debug)
            return 'error'


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
                                       #'version': None,
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


def get_r_package_class(package):
    global is_debug
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
            return None
        else:
            return label[:-1]
    except Exception as exc:
            raise
            #status_note(['! error while classifying r package:', exc.problem_mark, exc.problem], d=True)

