# pylint: skip-file
import pytest

def test_valid(script_runner, tmpdir):
    ret = script_runner.run('python3', 'o2rmeta.py', '-debug', 'validate',
        '-s', 'schema/json/o2r-meta-schema.json',
        '-c', 'schema/json/example_metadata_o2r_valid.json')
    print(ret.stdout)
    print(ret.stderr)

    assert ret.success, "process should return success"
    assert ret.stderr == '', "stderr should be empty"
    assert "against o2r-meta-schema.json" in ret.stdout, "should log used schema"
    assert "checking example_metadata_o2r_valid.json" in ret.stdout, "should log validated file"
    assert "valid: schema/json/example_metadata_o2r_valid.json" in ret.stdout, "should result in valid"

def test_dummy_invalid(script_runner, tmpdir):
    ret = script_runner.run('python3', 'o2rmeta.py', '-debug', 'validate',
        '-s', 'schema/json/o2r-meta-schema.json',
        '-c', 'schema/json/dummy.json')
    print(ret.stdout)
    print(ret.stderr)

    assert ret.success, "process should return success"
    assert ret.stderr == '', "stderr should be empty"
    assert "against o2r-meta-schema.json" in ret.stdout, "should log used schema"
    assert "checking dummy.json" in ret.stdout, "should log validated file"
    assert "!invalid" in ret.stdout, "should result in invalid"

def test_spacetime(script_runner, tmpdir):
    ret = script_runner.run('python3', 'o2rmeta.py', '-debug', 'validate',
        '-s', 'schema/json/o2r-meta-schema.json',
        '-c', 'validate/tests/spacetime.json')
    print(ret.stdout)
    print(ret.stderr)

    assert ret.success, "process should return success"
    assert ret.stderr == '', "stderr should be empty"
    assert "checking spacetime.json" in ret.stdout, "should log validated file"
    assert "invalid" not in ret.stdout, "should result in valid"

def test_minimal_rmd(script_runner, tmpdir):
    ret = script_runner.run('python3', 'o2rmeta.py', '-debug', 'validate',
        '-s', 'schema/json/o2r-meta-schema.json',
        '-c', 'validate/tests/minimal-rmd.json')
    print(ret.stdout)
    print(ret.stderr)

    assert ret.success, "process should return success"
    assert ret.stderr == '', "stderr should be empty"
    assert "checking minimal-rmd.json" in ret.stdout, "should log validated file"
    assert "invalid" not in ret.stdout, "should result in valid"
