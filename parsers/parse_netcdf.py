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
__all__ = ['ParseNetcdf']

from helpers.helpers import *

import netCDF4


FORMATS = ['.nc']
# FORMATS = ['.nc', '.cdl']


class ParseNetcdf:
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
            ncdf = netCDF4.Dataset(path_file)
            # todo: select properties, e.g. coordinates and pass to MD
            return None
        except Exception as exc:
            status_note(str(exc), d=True)


import netCDF4


a = netCDF4.Dataset("data/smith_sandwell_topo_v8_2.nc")

# try bbox

print(str(a.dimensions))
