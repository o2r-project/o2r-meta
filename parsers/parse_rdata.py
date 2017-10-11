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


from helpers.helpers import *

ID = 'o2r meta rdata parser'
FORMATS = ['.rdata']


class ParseRData:
    @staticmethod
    def get_id():
        return str(ID)

    @staticmethod
    def get_formats():
        return FORMATS

    def parse(self, **kwargs):
        p = filepath
        # skip large files, unsuitable for text preview
        if os.stat(filepath).st_size / 1024 ** 2 > 200:
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
                            status_note('invalid path to R executable', d=True)
                            rpath = None
                try:
                    if not os.path.exists(rpath):
                        # Cannot take path
                        status_note('fnc <get_rdata>] invalid path to R installation', d=True)
                        rpath = None
                except Exception as exc:
                    if is_debug:
                        raise
                    else:
                        pass
            else:
                status_note(rhome_name, d=True)
                rpath = None
        else:
            status_note([rhome_name, ' R_HOME env is not set...'], d=True)
            return None
        try:
            if rpath is None:
                return None
            status_note('processing RData')
            p = Popen([rpath, '--vanilla', os.path.abspath(filepath)], stdout=PIPE, stdin=PIPE, stderr=STDOUT)
            out = p.communicate(input=b'ls.str()')[0].decode('ISO-8859-1')[:-4].split("> ls.str()")[1]
            return out[:40000]
        except Exception as exc:
            status_note('! error while retrieving rdata', d=True)
            raise
