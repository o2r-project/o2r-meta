import json
import os
from jsonspec.validators import load #https://github.com/johnnoone/json-spec

#Main
if __name__ == "__main__":
    #Init
    my_path = os.path.join(os.path.dirname(os.getcwd()),'schema', 'json')
    my_schema = 'o2r-meta-schema.json'
    my_candidate = 'example1-valid.json'
    with open(os.path.join(my_path, my_schema)) as schema_file:
        that_schema = json.load(schema_file)
    with open(os.path.join(my_path, my_candidate)) as test_file:
        that_test = json.load(test_file)
    validator = load(that_schema)
    validator.validate(that_test)
