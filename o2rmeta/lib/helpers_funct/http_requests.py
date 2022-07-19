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

__all__ = ['get_ercspec_http', 'get_doi_http', 'get_orcid_http']

import json
import os
import urllib.request
import requests
from .helpers import *

ID = 'o2r meta http requester'
timeout = 3
user_agent = 'o2r-meta'
spec_url = 'https://o2r.info/erc-spec/erc-spec.pdf'


def get_id():
    return str(ID)


def get_ercspec_http(spec_output_dir, stay_offline):
    global user_agent
    global spec_url
    # use this function to configure a specification file that needs to be included
    if stay_offline:
        status_note('skipping erc spec download (http disabled)')
        return None
    else:
        try:
            spec_file = os.path.normpath(os.path.join(spec_output_dir, 'erc_spec.pdf'))
            status_note('downloading current erc spec')
            headers = {'User-Agent': user_agent}
            req = urllib.request.Request(spec_url, None, headers)
            http = urllib.request.urlopen(req, timeout=timeout).read()
            with open(spec_file, 'wb') as f:
                f.write(http)
            status_note(['saved <', spec_file, '>'], d=False)
        except urllib.error.HTTPError as hexc:
            status_note(['! failed to download and include spec:\n\t', spec_url, '\n\t', str(hexc)], d=True)
        except Exception as exc:
            status_note(['! failed to download and include spec: ', str(exc)], d=True)
            #raise


def get_doi_http(md_title, md_author, stay_offline):
    if stay_offline:
        status_note('skipping doi lookup (http disabled)')
        return None
    else:
        try:
            global timeout
            # via Crossref.org
            status_note('requesting doi via crossref.org ...')
            my_params = {'query.title': md_title, 'query.author': md_author}
            r = requests.get('https://api.crossref.org/works', params=my_params, timeout=timeout)
            status_note([r.status_code, ' ', r.reason])
            if r is not None:
                status_note('debug: <get_doi_http> GET', d=True)
                if 'message' in r.json():
                    if 'items' in r.json()['message']:
                        if type(r.json()['message']['items']) is list:
                            # take first hit, best match
                            if 'DOI' in r.json()['message']['items'][0]:
                                return r.json()['message']['items'][0]['DOI']
        except requests.exceptions.Timeout:
            status_note('http doi request: timeout')
        except requests.exceptions.TooManyRedirects:
            status_note('http doi request: too many redirects')
        except requests.exceptions.RequestException as e:
            status_note(['http doi request:', e])
        except Exception as exc:
            status_note('! error while requesting doi', d=True)
            raise


def get_orcid_http(txt_input, bln_sandbox, stay_offline):
    if stay_offline:
        status_note('skipping orcid lookup (http disabled)')
        return None
    else:
        try:
            global timeout
            status_note(['requesting orcid for <', txt_input, '>'])
            headers = {"Content-Type": "application/json"}
            my_params = {"q": txt_input}
            if bln_sandbox:
                r = requests.get('https://pub.sandbox.orcid.org/v2.0/search', params=my_params, headers=headers, timeout=timeout)
            else:
                r = requests.get('https://pub.orcid.org/v2.0/search', params=my_params, headers=headers, timeout=timeout)
            status_note([r.status_code, ' ', r.reason])
            if 'num-found' in r.json():
                if r.json()['num-found'] > 0:
                    if 'result' in r.json():
                        if type(r.json()['result']) is list:
                            if 'orcid-identifier' in r.json()['result'][0]:
                                if 'path' in r.json()['result'][0]['orcid-identifier']:
                                    return str(r.json()['result'][0]['orcid-identifier']['path'])
        except requests.exceptions.Timeout:
            status_note('http orcid request: timeout')
            return None
        except requests.exceptions.TooManyRedirects:
            status_note('http orcid request: too many redirects')
            return None
        except requests.exceptions.RequestException as e:
            status_note(['http orcid request: ', e])
            return None
        except Exception as exc:
            status_note('! error while requesting orcid', d=True)
            raise
