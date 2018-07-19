# pylint: skip-file
import pytest

def validate_mapping(path, script_runner):
    ret = script_runner.run('python3', 'o2rmeta.py', '-debug', 'validate',
        '-s', 'schema/json/map-schema.json',
        '-c', path)
    print(ret.stdout)
    print(ret.stderr)

    assert ret.success, "process should return success"
    assert ret.stderr == '', "stderr should be empty"
    assert "valid: " + path in ret.stdout, "mapping should be valid"

def test_o2r(script_runner, tmpdir):
    validate_mapping('broker/mappings/o2r-map.json', script_runner)

def test_b2share(script_runner, tmpdir):
    validate_mapping('broker/mappings/b2share-map.json', script_runner)

def test_b2share_sandbox(script_runner, tmpdir):
    validate_mapping('broker/mappings/b2share_sandbox-map.json', script_runner)

def test_codemeta(script_runner, tmpdir):
    validate_mapping('broker/mappings/codemeta-map.json', script_runner)

def test_zenodo(script_runner, tmpdir):
    validate_mapping('broker/mappings/zenodo-map.json', script_runner)

def test_zenodo_sandbox(script_runner, tmpdir):
    validate_mapping('broker/mappings/zenodo_sandbox-map.json', script_runner)
