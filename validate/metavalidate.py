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
import json
import os
import sys

#from jsonspec.validators import load #https://github.com/johnnoone/json-spec
import jsonspec.validators

#Main
if __name__ == "__main__":
    if sys.version_info[0] < 3:
        # py2
        print('[metavalidate] requires py3k or later')
        sys.exit()
    else:
        parser = argparse.ArgumentParser(description='description')
        parser.add_argument('-s', '--schema', help='path to schema', required=True)
        parser.add_argument('-c', '--candidate', help='path to candidate', required=True)
        args = parser.parse_args()
        argsdict = vars(args)
        my_schema = argsdict['schema']
        my_candidate = argsdict['candidate']
        print('[metavalidate] checking ' + os.path.basename(my_candidate))
        try:
            with open(os.path.abspath(my_schema), encoding='utf-8') as schema_file:
                that_schema = json.load(schema_file)
            with open(os.path.abspath(my_candidate), encoding='utf-8') as test_file:
                that_test = json.load(test_file)
            validator = jsonspec.validators.load(that_schema)
            validator.validate(that_test)
            print('[metavalidate] valid: ' + os.path.basename(my_candidate))
        except jsonspec.validators.exceptions.ValidationError as exc:
            print('[metavalidate] !invalid: ' + str(exc.errors))
        except:
            print('[metavalidate] error', sys.exc_info()[0])
            #raise