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

__all__ = ['ParseRData']

import os
from helpers.helpers import *
from subprocess import Popen, PIPE, STDOUT


try:
    import rpy2.robjects as robjects
    FORMATS = ['.rdata']
except ImportError as iexc:
    FORMATS = []
    availability_issues = str(iexc)


ID = 'o2r meta rdata parser'


class ParseRData:
    @staticmethod
    def get_id():
        return str(ID)

    @staticmethod
    def get_formats():
        if not FORMATS:
            status_note([__class__, ' unavailable (', str(availability_issues), ')'])
        return FORMATS

    @staticmethod
    def parse(**kwargs):
        path_file = kwargs.get('p', None)
        is_debug = kwargs.get('is_debug', None)
        MASTER_MD_DICT = kwargs.get('md', None)
        # skip large files, unsuitable for text preview
        if os.stat(path_file).st_size / 1024 ** 2 > 250:
            status_note('skipping large RData file...', d=True)
            return None
        try:
            rdata_dict = {path_file: {}}
            for key in robjects.r['load'](path_file):
                if key is not None and len(key) > 1:
                    rdata_dict[path_file].update(key)
            if 'rdata' in MASTER_MD_DICT:
                if 'rdata_files' in MASTER_MD_DICT['rdata']:
                    MASTER_MD_DICT['rdata']['rdata_files'].append(rdata_dict)
            return MASTER_MD_DICT
        except Exception as exc:
            status_note(str(exc), d=is_debug)
            status_note(['could not complete parsing ', str(path_file)], d=is_debug)
            return MASTER_MD_DICT
            #raise
