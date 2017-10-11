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
        try:
            txt_dict = {'bagittxt_file': path_file}
            with open(path_file) as f:
                lines = f.readlines()
                for line in lines:
                    s = line.rstrip('\n').split(': ')
                    txt_dict[s[0]] = s[1]
            MASTER_MD_DICT.update(txt_dict)
            return MASTER_MD_DICT
        except Exception as exc:
            raise
