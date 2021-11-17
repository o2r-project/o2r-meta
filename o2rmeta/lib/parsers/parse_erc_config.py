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

__all__ = ['ParseErcConfig']

import os
import yaml
from ..helpers_funct import helpers as help

ID = 'o2r erc configuration file (erc.yml) parser'

FORMATS = ['.yml']


class ParseErcConfig:
    @staticmethod
    def get_id():
        return str(ID)

    @staticmethod
    def get_formats():
        return FORMATS

    @staticmethod
    def parse(**kwargs):
        is_debug = False
        try:
            path_file = kwargs.get('p', None)
            MASTER_MD_DICT = kwargs.get('md', None)
            is_debug = kwargs.get('is_debug', None)

            global erc_id
            erc_id = None
            global erc_spec_version
            erc_spec_version = None
            global basedir
            basedir = kwargs.get('bd', None)

            erc_config = yaml.load(open(path_file),Loader=yaml.FullLoader)

            if erc_config is not None:
                # id and spec_version:
                if 'id' in erc_config:
                    if erc_config['id'] is not None:
                        MASTER_MD_DICT['id'] = erc_config['id']
                        erc_id = erc_config['id']
                if 'spec_version' in erc_config:
                    if erc_config['spec_version'] is not None:
                        erc_spec_version = erc_config['spec_version']
                help.status_note(['parsing ', path_file, ' for compendium ', erc_id,
                    ' with version ', erc_spec_version, ' and basedir ', basedir, ' :\n',
                    str(erc_config)], d=is_debug)

                # main and display file
                if 'main' in erc_config:
                    if erc_config['main'] is not None:
                        if basedir:
                            # relative path handling happens outside of parser for main
                            # erc.yml paths are by definition relative to erc.yml
                            abs_path = os.path.abspath(os.path.join(os.path.dirname(path_file), erc_config['main']))
                            MASTER_MD_DICT['mainfile'] = abs_path
                        else:
                            MASTER_MD_DICT['mainfile'] = erc_config['main']
                else:
                    help.status_note('warning: no main file in erc.yml', d=is_debug)
                if 'display' in erc_config:
                    if erc_config['display'] is not None:
                        if basedir:
                            # relative path handling for displayfile
                            abs_path = os.path.abspath(os.path.join(os.path.dirname(path_file), erc_config['display']))
                            MASTER_MD_DICT['displayfile'] = os.path.relpath(abs_path, basedir)
                        else:
                            MASTER_MD_DICT['displayfile'] = erc_config['display']
                else:
                    help.status_note('warning: no display file in erc.yml', d=is_debug)

                # licenses:
                if 'licenses' in erc_config:
                    if erc_config['licenses'] is not None:
                        MASTER_MD_DICT['license'] = erc_config['licenses']
                # convention:
                if 'convention' in erc_config:
                    if erc_config['convention'] is not None:
                        MASTER_MD_DICT['convention'] = erc_config['convention']
            else:
                help.status_note(['error parsing erc.yml from', str(path_file)], d=is_debug)

            return MASTER_MD_DICT
        except yaml.YAMLError as yexc:
            if hasattr(yexc, 'problem_mark'):
                if yexc.context is not None:
                    help.status_note(['yaml error\n\t', str(yexc.problem_mark), '\n\t', str(yexc.problem), ' ', str(yexc.context)], d=True)
                    return 'error'
                else:
                    help.status_note(['yaml error\n\t', str(yexc.problem_mark), '\n\t', str(yexc.problem)],
                        d=is_debug)
                return 'error'
            else:
                help.status_note(['! error: unable to parse yaml \n\t', str(yexc)], d=is_debug)
                return 'error'
        except Exception as exc:
            help.status_note(str(exc), d=is_debug)
            return 'error'
