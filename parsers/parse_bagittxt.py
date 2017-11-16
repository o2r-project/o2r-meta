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

__all__ = ['ParseBagitTxt']


from helpers.helpers import *

ID = 'o2r meta bagit txt parser'
FORMATS = ['.txt']


class ParseBagitTxt:
    @staticmethod
    def get_id():
        return str(ID)

    @staticmethod
    def get_formats():
        return FORMATS

    def parse(self, **kwargs):
        path_file = kwargs.get('p', None)
        MASTER_MD_DICT = kwargs.get('md', None)
        is_debug = kwargs.get('is_debug', None)
        try:
            if not path_file.endswith('bagit.txt'):
                return None
            txt_dict = {path_file: {}}
            with open(path_file) as f:
                lines = f.readlines()
                for line in lines:
                    s = line.rstrip('\n').split(': ')
                    txt_dict[path_file].update({str(s[0]): str(s[1])})
            if 'bagit' in MASTER_MD_DICT:
                if 'bagittxt_files' in MASTER_MD_DICT['bagit']:
                    MASTER_MD_DICT['bagit']['bagittxt_files'].append(txt_dict)
                MASTER_MD_DICT['provenance'] = get_prov(path_file)
            return MASTER_MD_DICT
        except Exception as exc:
            status_note(str(exc), d=is_debug)
            return 'error'
