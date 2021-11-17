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

__all__ = ['ParseCandidateFiles']

import os
from ..helpers_funct import helpers

ID = 'o2r meta candidate file parser'
# formats includes displayfile extensions and codefile extensions, seperation will take place in parse func.
FORMATS = ['.html', '.htm', '.png', '.pdf', '.r', '.rmd', '.js', '.py']


class ParseCandidateFiles:
    @staticmethod
    def get_id():
        return str(ID)

    @staticmethod
    def get_formats():
        return FORMATS

    @staticmethod
    def parse(**kwargs):
        try:
            MASTER_MD_DICT = kwargs.get('md', None)
            path_file = kwargs.get('p', None)
            is_debug = kwargs.get('is_debug', None)
            extension = kwargs.get('ext', None)
            basedir = kwargs.get('bd', None)
            MASTER_MD_DICT = add_candidates('codefiles', extension, ['.r', '.rmd', '.js', '.py'], MASTER_MD_DICT, path_file, basedir)
            MASTER_MD_DICT = add_candidates('displayfile_candidates', extension, ['.html', '.htm', '.png', 'pdf'], MASTER_MD_DICT, path_file, basedir)
            MASTER_MD_DICT = add_candidates('mainfile_candidates', extension, ['.r', '.rmd'], MASTER_MD_DICT, path_file, basedir)
            return MASTER_MD_DICT
        except Exception as exc:
            status_note('! error while listing display files', d=is_debug)
            return 'error'

def add_candidates(key_name, extension, extensions_list, master_dict, path_file, basedir):
    if key_name in master_dict:
        if os.path.isfile(path_file):
            if extension in extensions_list:
                master_dict[key_name].append(os.path.normpath(os.path.relpath(path_file, basedir)))
    return master_dict
