"""
    Copyright (c) 2016-2018 - o2r project

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
from .lib import metaextract as metaextract
from .lib import metabroker as metabroker
from .lib import metavalidate as metavalidate
from .lib import metaharvest as metaharvest
from .lib.helpers_funct import helpers as help

import argparse
import sys

def main():
    try:
        parser = argparse.ArgumentParser(description='description')
        parser.add_argument('-debug', help='debug mode', action='store_true', default=False, required=False)
        subparsers = parser.add_subparsers(title='extractor', dest='tool')
        # - - - - - - - - - - - - - - - - - -
        extractor = subparsers.add_parser("extract")
        extractor.add_argument('-f', '--formats', help='show supported formats', action='store_true', default=False)
        extractor.add_argument('-i', '--inputdir', type=str)
        group = extractor.add_mutually_exclusive_group()
        group.add_argument('-o', '--outputdir', type=str, help='output directory for extraction docs')
        group.add_argument('-s', '--outputtostdout', help='output the result of the extraction to stdout',
                           action='store_true', default=False)
        extractor.add_argument('-e', '--ercid', type=str, help='erc identifier')
        extractor.add_argument('-b', '--basedir', type=str, help='base directory for relative paths')
        extractor.add_argument('-xml', '--modexml', help='output xml', action='store_true', default=False, required=False)
        extractor.add_argument('-xo', '--stayoffline', help='skip all http requests', action='store_true', default=False)
        extractor.add_argument('-m', '--metafiles', help='output all metafiles', action='store_true', default=False)
        extractor.add_argument('-lic', '--default-metadata-license', help='the license to use for metadata if none is found', type=str)
        # - - - - - - - - - - - - - - - - - -
        # the broker has two modes:
        # 1.) mapping mode creates fitting metadata for a given map
        # 2.) checking mode returns missing metadata information for a target service
        broker = subparsers.add_parser("broker")
        maingroup = broker.add_mutually_exclusive_group(required=True)
        maingroup.add_argument('-c', '--check', type=str, required=False)
        maingroup.add_argument('-m', '--map', type=str, required=False)
        broker.add_argument('-i', '--inputfile', type=str, required=True)
        group = broker.add_mutually_exclusive_group(required=True)
        group.add_argument('-o', '--outputdir', type=str, help='output directory for brokering docs')
        group.add_argument('-s', '--outputtostdout', help='output the result of the brokering to stdout',
                           action='store_true', default=False)
        # - - - - - - - - - - - - - - - - - -
        harvester = subparsers.add_parser("harvest")
        harvester.add_argument('-e', '--element', type=str,  help='element type, e.g. doi or creator',required=True)
        harvester.add_argument('-q', '--query', type=str,  help='query string', required=True)
        # - - - - - - - - - - - - - - - - - -
        validator = subparsers.add_parser("validate")
        validator.add_argument('-s', '--schema', type=str, required=True)
        validator.add_argument('-c', '--candidate', type=str, required=True)
        # - - - - - - - - - - - - - - - - - -
        args = parser.parse_args()
        argsd = vars(args)
        help.status_note(['received arguments: ', argsd], d=False)
        if argsd['tool'] == "extract":
            if argsd['formats']:
                metaextract.get_formats(dbg=argsd['debug'])
                sys.exit(0)
            else:
                help.status_note('launching extractor')
                metaextract.start(dbg=argsd['debug'],
                    i=argsd['inputdir'],
                    o=argsd['outputdir'],
                    s=argsd['outputtostdout'],
                    xo=argsd['stayoffline'],
                    e=argsd['ercid'],
                    f=argsd['formats'],
                    b=argsd['basedir'],
                    m=argsd['metafiles'],
                    xml=argsd['modexml'],
                    lic=argsd['default_metadata_license'])
        elif argsd['tool'] == "broker":
            help.status_note('launching broker')
            metabroker.start(dbg=argsd['debug'], c=argsd['check'], m=argsd['map'], i=argsd['inputfile'], o=argsd['outputdir'], s=argsd['outputtostdout'])
        elif argsd['tool'] == "validate":
            help.status_note('launching validator')
            metavalidate.start(s=argsd['schema'], c=argsd['candidate'])
        elif argsd['tool'] == "harvest":
            help.status_note('launching harvester')
            metaharvest.start(e=argsd['element'], q=argsd['query'])
    except Exception as exc:
        raise

if __name__ == '__main__':
    main()
