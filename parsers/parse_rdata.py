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

ID = 'o2r meta rdata parser'
FORMATS = ['.rdata']


class ParseRData:
    @staticmethod
    def get_id():
        return str(ID)

    @staticmethod
    def get_formats():
        return FORMATS

    @staticmethod
    def parse(**kwargs):
        path_file = kwargs.get('p', None)
        is_debug = kwargs.get('is_debug', None)
        # skip large files, unsuitable for text preview
        if os.stat(path_file).st_size / 1024 ** 2 > 250:
            status_note('skipping large RData file...', d=True)
            return None
        rhome_name = 'R_HOME'
        if rhome_name in os.environ:
            if os.environ[rhome_name] is not None:
                # OK try R_HOME value
                rpath = os.environ[rhome_name].replace("\\", "/")
                # add executable to path
                if not rpath.endswith('R') and not rpath.endswith('R.exe'):
                    if os.path.exists(os.path.join(rpath, 'R.exe')):
                        rpath = os.path.join(rpath, 'R.exe')
                    else:
                        if os.path.exists(os.path.join(rpath, 'R')):
                            rpath = os.path.join(rpath, 'R')
                        else:
                            # Cannot take path
                            status_note('cannot parse .data file, R_HOME not configured or invalid path to R executable', d=is_debug)
                            rpath = None
                try:
                    if rpath is not None:
                        if not os.path.exists(rpath):
                            # Cannot take path
                            status_note('cannot parse .data file, invalid path to R installation', d=is_debug)
                            rpath = None
                except Exception as exc:
                    status_note(['! error parsing rdata', str(exc)], d=is_debug)
            else:
                status_note(rhome_name, d=True)
                rpath = None
        else:
            status_note([rhome_name, 'cannot parse .rdata file, R_HOME not configured'], d=is_debug)
            return None
        try:
            if rpath is None:
                return None
            status_note('processing RData')
            p = Popen([rpath, '--vanilla', os.path.abspath(path_file)], stdout=PIPE, stdin=PIPE, stderr=STDOUT)
            out = p.communicate(input=b'ls.str()')[0].decode('ISO-8859-1')[:-4].split("> ls.str()")[1]
            return out[:40000]
        except Exception as exc:
            status_note(str(exc), d=True)
            raise
