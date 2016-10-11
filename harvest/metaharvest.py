'''
    Copyright (c) 2016 - o2r project

    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at

        http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.

'''

import argparse
import base64
import sys
import urllib.request


def qu(q_type,q_string,q_base):
    accepted = ['doi','creator']
    if q_type in accepted:
        # datacite solr query encoding ideolect:
        my_query = str.encode('q='+q_type+'%3A'+q_string)
        encoded = base64.urlsafe_b64encode(my_query)
        encoded = str(encoded, 'utf-8').replace('=', '')
        my_url = q_base + encoded
        headers = {}
        req = urllib.request.Request(my_url, None, headers)
        http = urllib.request.urlopen(req).read()
        # save as file
        #my_file = 'test.txt'
        #with open(my_file, 'wb') as f:
        #    f.write(http)
        # print to screen
        print(str(http, 'utf-8'))
    else:
        print('query type not available')
        return None

# main:
if __name__ == "__main__":
    if sys.version_info[0] < 3:
        # py2
        print('requires py3k or later')
        sys.exit()
    else:
        parser = argparse.ArgumentParser(description='description')
        parser.add_argument('-t', '--typequery', help='query type, e.g. doi or creator', required=True)
        parser.add_argument('-q', '--query', help='searched string for that type', required=True)
        args = parser.parse_args()
        argsdict = vars(args)
        t = argsdict['typequery']
        q = argsdict['query']
        #inits
        datacite_base = 'http://oai.datacite.org/oai?verb=ListRecords&metadataPrefix=oai_datacite&set=~'
        crossref_base = 'http://oai.crossref.org/OAIHandler?verb='
        # http://doi.crossref.org/schemas/unixref1.1.xsd
        print('starting request')
        # currently using datacite
        qu(t,q,datacite_base)