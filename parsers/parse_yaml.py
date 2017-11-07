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
    def internal_parse(input_text, MASTER_MD_DICT, stay_offline):
        # This is for R markdown files with yaml headers
        try:
            yaml_data_dict = yaml.safe_load(input_text)
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
                                yaml_data_dict['orcid'] = id_found
                                MASTER_MD_DICT['author'].append({'affiliation': [], 'name': author_name, 'orcid': id_found})
                        else:
                            # author tag is present and string, but no concatenation
                            id_found = get_orcid_http(yaml_data_dict['author'], False, stay_offline)
                            yaml_data_dict['orcid'] = id_found
                            MASTER_MD_DICT['author'].append(
                                {'affiliation': [], 'name': yaml_data_dict['author'], 'orcid': id_found})
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
                                # todo: stop using sandbox for orcid retrieval
                                anyone['orcid'] = get_orcid_http(anyone['name'], True, stay_offline)
                # model date:
                if 'date' in yaml_data_dict:
                    try:
                        #parse_temporal(None, None, CANDIDATES_MD_DICT, yaml_data_dict['date'])
                        pass
                    except Exception as exc:
                        status_note(['! failed to parse temporal <', yaml_data_dict['date'], '> (', str(exc.args[0]), ')'], d=True)
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
                if 'runtime' in yaml_data_dict:
                    if yaml_data_dict['runtime'] == 'shiny' and 'interaction' in MASTER_MD_DICT:
                        MASTER_MD_DICT['interaction']['interactive'] = True
            return yaml_data_dict
        except yaml.YAMLError as yexc:
                status_note(['! error while parsing yaml input:', str(yexc)], d=True)
                raise
        except Exception as exc:
            status_note('! error while parsing yaml', d=True)
            raise
