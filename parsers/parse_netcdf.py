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

try:
    from netCDF4 import *
    FORMATS = ['.nc']
except ImportError as iexc:
    FORMATS = []
    availability_issues = str(iexc)

ID = 'o2r meta netcdf parser'



class ParseNetcdf:
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
        is_debug = False
        try:
            path_file = kwargs.get('p', None)
            MASTER_MD_DICT = kwargs.get('md', None)
            is_debug = kwargs.get('is_debug', None)
            ncdf = netCDF4.Dataset(path_file)
            ncdf_dict = {path_file: {}}
            ncdf_dict[path_file].update(extract_netcdf_dataset_str(ncdf.variables))
            ncdf_dict[path_file].update(extract_netcdf_dataset_str(ncdf.dimensions))
            if 'ncdf' in MASTER_MD_DICT:
                if 'ncdf_files' in MASTER_MD_DICT['ncdf']:
                    MASTER_MD_DICT['ncdf']['ncdf_files'].append(ncdf_dict)
            return MASTER_MD_DICT
        except Exception as exc:
            #raise  # remove
            status_note(str(exc), d=is_debug)
            return 'error'


def extract_netcdf_dataset_str(dataset):
    # todo except datasets too large to process (currently covered by metaextract config max filesize
    data_dict = {}
    try:
        from collections import OrderedDict
        if type(dataset) in [list, dict, OrderedDict]:
            for key in dataset:
                block = dataset[key]
                lines = str(block).split('\n')
                for line in lines:
                    value = line.split(':')
                    if len(value) > 1:
                        if not str(value[0].strip()).startswith('<'):
                            data_dict[value[0].strip()] = value[1].strip()
    except:
        #raise  # remove
        return
    return data_dict
