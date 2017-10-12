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
__all__ = ['ParseGeojson']

import json

ID = 'o2r meta geojson parser'
FORMATS = ['.geojson']


class ParseGeojson:
    @staticmethod
    def get_id():
        return str(ID)

    @staticmethod
    def get_formats():
        return FORMATS

    #def parse(self):
    #    pass


# todo overhaul
def extract_spatial(filepath, fformat):
    try:
        # <side_key> is an dict key in candidates to store all spatial files as list, other than finding the best candidate of spatial file
        side_key = 'global_spatial'
        if side_key not in CANDIDATES_MD_DICT:
            CANDIDATES_MD_DICT[side_key] = {}
        # work on formats:
        coords = None
        if fformat == '.geojson':
            #todo: bbox extraction
            return None
        elif fformat == '.json':
            #todo: check if geojson
            return None
        else:
            # all other file extensions: exit
            return None
        # prepare json object:
        new_file_key = {}
        if 'spatial' not in CANDIDATES_MD_DICT[side_key]:
            CANDIDATES_MD_DICT[side_key] = {}
        if 'files' not in CANDIDATES_MD_DICT[side_key]:
            key_files = {'files': []}
            CANDIDATES_MD_DICT[side_key] = key_files
        new_file_key['source_file'] = get_rel_path(filepath)
        new_file_key['geojson'] = {'type': 'Feature',
                                   'geometry': {}
                                }
        if coords is not None:
            new_file_key['geojson']['bbox'] = coords.bounds
            new_file_key['geojson']['geometry']['coordinates'] = [
                [[coords.bounds[0], coords.bounds[1]], [coords.bounds[2], coords.bounds[3]]]]
            new_file_key['geojson']['geometry']['type'] = 'Polygon'
            CANDIDATES_MD_DICT[side_key]['files'].append(new_file_key)
        # calculate union of all available coordinates
        # calculate this only once, at last
        current_coord_list = []
        for key in CANDIDATES_MD_DICT[side_key]['files']:
            if 'geojson' in key:
                if 'geometry' in key['geojson']:
                    if 'coordinates' in key['geojson']['geometry']:
                        if len(key['geojson']['geometry']['coordinates']) > 0:
                            current_coord_list.append((key['geojson']['geometry']['coordinates'][0][0]))
                            current_coord_list.append((key['geojson']['geometry']['coordinates'][0][1]))
        key_union = {}
        coords = calculate_geo_bbox_union(current_coord_list)
        key_union['geojson'] = {}
        if coords is not None:
            key_union['geojson']['bbox'] = [coords[0][0], coords[0][1], coords[1][0], coords[1][1]]
        key_union['geojson']['type'] = 'Feature'
        key_union['geojson']['geometry'] = {}
        key_union['geojson']['geometry']['type'] = 'Polygon'
        if coords is not None:
            key_union['geojson']['geometry']['coordinates'] = coords
        CANDIDATES_MD_DICT[side_key].update({'union': key_union})
    except Exception as exc:
        status_note(str(exc), d=True)


def calculate_geo_bbox_union(coordinate_list):
    global is_debug
    try:
        if coordinate_list is None:
            return [(0, 0), (0, 0), (0, 0), (0, 0)]
        min_x = 181.0
        min_y = 181.0
        max_x = -181.0
        max_y = -181.0
        ##max =[181.0, 181.0, -181.0, -181.0]  # proper max has -90/90 & -180/180
        # todo: deal with international date line wrapping / GDAL
        for n in coordinate_list:
            if n[0] < min_x:
                min_x = n[0]
            if n[0] > max_x:
                max_x = n[0]
            if n[1] < min_y:
                min_y = n[1]
            if n[1] > max_y:
                max_y = n[1]
        return [(min_x, min_y), (max_x, min_y), (max_x, max_y), (min_x, max_y)]
    except Exception as exc:
        status_note(str(exc), d=True)
