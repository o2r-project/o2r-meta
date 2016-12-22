"""
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

"""

import argparse
import base64
import json
import sys
import urllib.request
import datetime
import os

from lxml import etree


def parse_from_unicode(unicode_str):
    s = unicode_str.encode('utf-8')
    return etree.fromstring(s, parser=utf8_parser)


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
        return str(http, 'utf-8')
    else:
        print('query type not available')
        return None


def status_note(msg):
    print(''.join(('[metavharvest] ', msg)))


# main:
if __name__ == "__main__":
    if sys.version_info[0] < 3:
        # py2
        print('requires py3k or later')
        sys.exit()
    else:
        my_version = 1
        my_mod = ''
        try:
            my_mod = datetime.datetime.fromtimestamp(os.stat(__file__).st_mtime)
        except OSError:
            pass
        status_note(''.join(('v', str(my_version), ' - ', str(my_mod))))
        parser = argparse.ArgumentParser(description='description')
        parser.add_argument('-i', '--input', help='type of provided metadata element for input, e.g. doi or creator', required=True)
        parser.add_argument('-q', '--query', help='query string', required=True)
        args = parser.parse_args()
        argsdict = vars(args)
        i = argsdict['input']
        q = argsdict['query']
        #inits
        # load map for datacite
        try:
            with open('bases.json', encoding='utf-8') as data_file:
                bases = json.load(data_file)
                settings_data = bases['Settings']
                baseurl_data = bases['BaseURLs']
        except:
            raise
        print('[metaharvest] starting request')
        #test datacite
        result = qu(i.lower(),q,baseurl_data['DataCite']['url'])
        try:
            print('[metaharvest]' + result[:128])
            print('[metaharvest] ...')
            utf8_parser = etree.XMLParser(encoding='utf-8')
            tree = parse_from_unicode(result)
            # e.g. return author from datacite creatorName
            output = {}
            for node in tree.xpath('//ns:creatorName', namespaces={'ns': 'http://datacite.org/schema/kernel-3'}):
                output['authorName'] = node.text
            json_output = json.dumps(output)
            #output if not empty
            if str(json_output) != '{}':
                print(str(json_output))
        except:
            raise
            #pass