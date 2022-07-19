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
__all__ = ["ParseSpatialFile"]

import geoextent.lib.extent as geoextent
from ..helpers_funct import helpers as help

ID = 'o2r meta geospatial parser'
FORMATS = [".geojson", ".csv", ".geotiff", ".tif", ".gpkg", ".shp", ".gpx", ".gml", ".nc", ".kml"]


# Declare your class
class ParseSpatialFile:
    @staticmethod
    def get_id():
        return str(ID)

    @staticmethod
    def get_formats():
        return FORMATS

    @staticmethod
    def parse(**kwargs):
        try:
            path_file = kwargs.get('p', None)
            MASTER_MD_DICT = kwargs.get('md', None)
            is_debug = kwargs.get('is_debug', None)

            extent = geoextent.fromFile(path_file, bbox=True)

            if 'spatial' in MASTER_MD_DICT:
                if 'files' in MASTER_MD_DICT['spatial']:
                    if extent.get("bbox") is not None:
                        MASTER_MD_DICT['spatial']['files'].append({"name": path_file,
                                                                   "bbox": extent.get("bbox"),
                                                                   "crs": extent.get("crs")})
            return MASTER_MD_DICT
        except Exception as exc:
            help.status_note(['! error while parsing spatial file ', str(exc)], d=is_debug)
