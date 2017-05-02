import base64
import json
import urllib.request

from lxml import etree


def parse_from_unicode(unicode_str):
    utf8_parser = etree.XMLParser(encoding='utf-8')
    s = unicode_str.encode('utf-8')
    return etree.fromstring(s, parser=utf8_parser)

def qu(q_type,q_string,q_base):
    # check if json url has been parsed correctly
    if q_base.startswith('\\url{'):
        q_base = q_base[5:].replace('}', '')
    accepted = ['doi', 'creator']
    if q_type in accepted:
        # datacite solr query encoding ideolect:
        my_query = str.encode('q='+q_type+'%3A'+q_string)
        encoded = base64.urlsafe_b64encode(my_query)
        encoded = str(encoded, 'utf-8').replace('=', '')
        my_url = q_base + encoded
        headers = {}
        req = urllib.request.Request(my_url, None, headers)
        http = urllib.request.urlopen(req).read()
        return(str(http, 'utf-8'))
    else:
        print('query type not available')
        return None


def status_note(msg):
    print(''.join(('[o2rmeta][harvest] ', str(msg))))


# main:
def start(**kwargs):
    global e
    e = kwargs.get('e', None)
    global q
    q = kwargs.get('q', None)
    try:
        with open('harvest/bases.json', encoding='utf-8') as data_file:
            bases = json.load(data_file)
            settings_data = bases['Settings']
            baseurl_data = bases['BaseURLs']
    except:
        raise
    status_note('new request')
    # demo datacite
    my_base = 'DataCite'
    # todo: argparse base endpoint
    try:
        result = qu(e.lower(), q, baseurl_data[my_base]['url'] + baseurl_data[my_base]['default_parameter'])
        status_note('!debug using ' + result[:256] + ' ...')
        tree = parse_from_unicode(result)
        # e.g. return author from datacite creatorName
        output = {}
        for node in tree.xpath('//ns:creatorName', namespaces={'ns': 'http://datacite.org/schema/kernel-3'}):
            output['authorName'] = node.text
        json_output = json.dumps(output)
        # output if not empty
        if str(json_output) != '{}':
            print(str(json_output))
    except:
        raise
