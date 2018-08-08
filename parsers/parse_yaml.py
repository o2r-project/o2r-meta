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

__all__ = ['ParseYaml']

import yaml
from helpers.helpers import *
from helpers.http_requests import *
from dateutil import parser as dateparser

ID = 'o2r meta yaml parser'
FORMATS = []


class ParseYaml:
    @staticmethod
    def get_id():
        return str(ID)

    @staticmethod
    def get_formats():
        return FORMATS

    @staticmethod
    def internal_parse(input_text, MASTER_MD_DICT, stay_offline, is_debug):
        # This is for R markdown files with yaml headers
        try:
            yaml_data_dict = yaml.load(input_text)
            if yaml_data_dict is not None:
                # model description / abstract:
                if 'description' in yaml_data_dict:
                    if yaml_data_dict['description'] is not None:
                        MASTER_MD_DICT['description'] = yaml_data_dict['description']
                else:
                    if 'abstract' in yaml_data_dict:
                        MASTER_MD_DICT['description'] = yaml_data_dict['abstract']
                # model author:
                if 'author' in yaml_data_dict:
                    if type(yaml_data_dict['author']) is str:
                        # todo: split multi author tag at <,> and or <and>
                        if ',' in yaml_data_dict['author']:
                            for author_name in yaml_data_dict['author'].split(', '):
                                id_found = get_orcid_http(author_name, False, stay_offline)
                                if id_found is not None:
                                    status_note(['orcid found for ', yaml_data_dict['author'], ': ', id_found], d=is_debug)
                                    yaml_data_dict['orcid'] = id_found
                                    MASTER_MD_DICT['author'].append({'affiliation': [], 'name': author_name, 'orcid': id_found})
                                else:
                                    status_note(['no orcid found for ', yaml_data_dict['author']], d=is_debug)
                                    MASTER_MD_DICT['author'].append({'affiliation': [], 'name': author_name})
                        else:
                            # author tag is present and string, but no concatenation
                            id_found = get_orcid_http(yaml_data_dict['author'], False, stay_offline)
                            if id_found is not None:
                                status_note(['orcid found for ', yaml_data_dict['author'], ': ', id_found], d=is_debug)
                                yaml_data_dict['orcid'] = id_found
                                MASTER_MD_DICT['author'].append({'affiliation': [], 'name': yaml_data_dict['author'], 'orcid': id_found})
                            else:
                                status_note(['no orcid found for ', yaml_data_dict['author']], d=is_debug)
                                MASTER_MD_DICT['author'].append({'affiliation': [], 'name': yaml_data_dict['author']})
                        if 'affiliation' not in yaml_data_dict:
                            # we have author but miss affiliation, so add empty list
                            yaml_data_dict['affiliation'] = []
                        else:
                            # we have affiliation but not an empty list, so make empty list
                            if yaml_data_dict['affiliation'] is None:
                                yaml_data_dict['affiliation'] = []
                            else:
                                if type(yaml_data_dict['affiliation']) is list:
                                    yaml_data_dict['affiliation'] = yaml_data_dict['affiliation'][0]
                    elif type(yaml_data_dict['author']) is list:
                        for anyone in yaml_data_dict['author']:
                            if 'name' in anyone:
                                if not 'orcid' in anyone:
                                    id_found = get_orcid_http(anyone['name'], False, stay_offline)
                                    if id_found is not None:
                                        status_note(['orcid found for ', anyone['name'], ': ', id_found], d=is_debug)
                                        anyone['orcid'] = id_found
                # model date:
                if 'date' in yaml_data_dict:
                    try:
                        extract_temporal(None, None, MASTER_MD_DICT, yaml_data_dict['date'], is_debug)
                    except Exception as exc:
                        status_note(['! unable to parse temporal <', yaml_data_dict['date'], '> (', str(exc), ')'], d=is_debug)
                # model doi:
                this_doi = None
                if 'doi' in yaml_data_dict:
                    this_doi = yaml_data_dict['doi']
                if 'DOI' in yaml_data_dict:
                    this_doi = yaml_data_dict['DOI']
                # other doi source is http request, and will be done later if title + author name is available
                if this_doi is not None:
                    # the author might have used the doi tag but added a doi url instead:
                    if this_doi.startswith('http'):
                        MASTER_MD_DICT['identifier']['doi'] = this_doi.split('.org/')[1]
                        MASTER_MD_DICT['identifier']['doiurl'] = this_doi
                    else:
                        MASTER_MD_DICT['identifier']['doi'] = this_doi
                        MASTER_MD_DICT['identifier']['doiurl'] = ''.join(('https://doi.org/', this_doi))
                # model keywords:
                if 'keywords' in yaml_data_dict:
                    # reduce to plain keyword list if given
                    if 'plain' in yaml_data_dict['keywords']:
                        yaml_data_dict['keywords'] = yaml_data_dict['keywords']['plain']
                # model keywords:
                if 'title' in yaml_data_dict:
                    # reduce to plain title list if given
                    if 'plain' in yaml_data_dict['title']:
                        yaml_data_dict['title'] = yaml_data_dict['title']['plain']
                # model interaction / shiny:
                #if 'runtime' in yaml_data_dict:
                #    if yaml_data_dict['runtime'] == 'shiny' and 'interaction' in MASTER_MD_DICT:
                #        MASTER_MD_DICT['interaction']['interactive'] = True
                # licenses:
                if 'licenses' in yaml_data_dict:
                    if yaml_data_dict['licenses'] is not None:
                        extracted_licenses = yaml_data_dict['licenses']
                        status_note(['Found licenses: ', str(extracted_licenses)], d=is_debug)
                        if 'code' in extracted_licenses and extracted_licenses['code'] is not None:
                            MASTER_MD_DICT['license']['code'] = extracted_licenses['code']
                        if 'data' in extracted_licenses and extracted_licenses['data'] is not None:
                            MASTER_MD_DICT['license']['data'] = extracted_licenses['data']
                        if 'text' in extracted_licenses and extracted_licenses['text'] is not None:
                            MASTER_MD_DICT['license']['text'] = extracted_licenses['text']
                        if 'metadata' in extracted_licenses and extracted_licenses['metadata'] is not None:
                            MASTER_MD_DICT['license']['metadata'] = extracted_licenses['metadata']
                        
                        MASTER_MD_DICT['license'] = {k:v for k,v in MASTER_MD_DICT['license'].items() if v is not None}    
                        status_note(['Final extracted licenses: ', str(MASTER_MD_DICT['license'])], d=is_debug)
            return yaml_data_dict
        except yaml.YAMLError as yexc:
            if hasattr(yexc, 'problem_mark'):
                if yexc.context is not None:
                    status_note(['yaml error\n\t', str(yexc.problem_mark), '\n\t', str(yexc.problem), ' ', str(yexc.context)], d=True)
                    return 'error'
                else:
                    status_note(['yaml error\n\t', str(yexc.problem_mark), '\n\t', str(yexc.problem)], d=is_debug)
                return 'error'
            else:
                status_note(['! error: unable to parse yaml \n\t', str(yexc)], d=is_debug)
                return 'error'


def extract_temporal(file_id, filepath, data, timestamp, is_debug):
    global date_new
    date_new = None
    try:
        if timestamp is not None:
            try:
                # try parse from string, but input is potentially r code
                date_new = dateparser.parse(timestamp).isoformat()
            except Exception as exc:
                status_note(['! error while parsing date', str(exc)], d=is_debug)
        else:
            if filepath is not None:
                date_new = str(datetime.datetime.fromtimestamp(os.stat(filepath).st_mtime).isoformat())
        if data is not None:
            if 'temporal' in data and date_new is not None:
                if 'begin' in data['temporal'] and 'end' in data['temporal']:
                    date_earliest = data['temporal']['begin']
                    if date_earliest is not None:
                        if date_new < date_earliest:
                            # new candidate is earlier than earliest
                            data['temporal'].update({'begin': date_new})
                    else:
                        # nothing yet, so take this one
                        data['temporal'].update({'begin': date_new})
                    date_latest = data['temporal']['end']
                    if date_latest is not None:
                        if date_new > date_latest:
                            # new candidate is later than latest
                            data['temporal'].update({'end': date_new})
                    else:
                        # nothing yet, so take this one
                        data['temporal'].update({'end': date_new})
    except Exception as exc:
        status_note(str(exc), d=is_debug)
