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
__all__ = ['ParseGeopackage']

from helpers.helpers import *


try:
    from fiona import *
    FORMATS = ['.gpkg', '.shp']
except ImportError as iexc:
    FORMATS = []
    availability_issues = str(iexc)


ID = 'o2r meta ogc geopackage and shapefile parser'


class ParseGeopackage:
    @staticmethod
    def get_id():
        return str(ID)

    @staticmethod
    def get_formats():
        if not FORMATS:
            status_note([__class__, ' unavailable (', str(availability_issues), ')'])
        return FORMATS

    @staticmethod
    def get_availability():
        return available

    @staticmethod
    def parse(**kwargs):
        try:
            path_file = kwargs.get('p', None)
            MASTER_MD_DICT = kwargs.get('md', None)
            is_debug = kwargs.get('is_debug', None)
            # todo: add extractions
            return MASTER_MD_DICT
        except Exception as exc:
            status_note(['! error while parsing geopackge ', str(exc)], d=is_debug)
