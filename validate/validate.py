import argparse
import json
import os

from jsonspec.validators import load #https://github.com/johnnoone/json-spec

#Main
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='description')
    parser.add_argument('-s', '--schema', help='path to schema', required=True)
    parser.add_argument('-c', '--candidate', help='path to candidate', required=True)
    args = parser.parse_args()
    argsdict = vars(args)
    #expl: -s"../schema/json/o2r-meta-schema.json" -c"../schema/json/example1-valid.json"
    my_schema = argsdict['schema']
    my_candidate = argsdict['candidate']
    with open(os.path.abspath(my_schema)) as schema_file:
        that_schema = json.load(schema_file)
    with open(os.path.abspath(my_candidate)) as test_file:
        that_test = json.load(test_file)
    validator = load(that_schema)
    validator.validate(that_test)