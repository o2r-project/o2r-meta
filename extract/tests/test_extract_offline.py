# pylint: skip-file
import pytest
import json
import os

def test_offline(script_runner, tmpdir):
    ret = script_runner.run('python3', 'o2rmeta.py', 'extract', 
        '-i', 'extract/tests/carberry',
        '-o', str(tmpdir),
        '-xo')
    assert ret.success, "process should return success"
    assert "http disabled" in ret.stdout, "should log not going online"
    assert ret.stderr == '', "stderr should be empty"

def test_online(script_runner, tmpdir):
    ret = script_runner.run('python3', 'o2rmeta.py', 'extract', 
        '-i', 'extract/tests/carberry',
        '-o', str(tmpdir))
    assert ret.success, "process should return success"
    assert "http disabled" not in ret.stdout, "should not log staying offline"
    assert "downloading current erc spec" in ret.stdout, "should log downloading spec"
    assert ret.stderr == '', "stderr should be empty"

def test_offline_no_orcid(script_runner, tmpdir):
    ret = script_runner.run('python3', 'o2rmeta.py', '-debug', 'extract', 
        '-i', 'extract/tests/minimal',
        '-o', str(tmpdir),
        '-xo')
    assert ret.success, "process should return success"
    assert "http disabled" in ret.stdout, "should log not going online"
    assert ret.stderr == '', "stderr should be empty"

    metadata = json.load(open(os.path.join(str(tmpdir), 'metadata_raw.json')))
    assert "orcid" not in metadata['author'][0], "should not have orcid entry in authors"

def test_online_with_orcid(script_runner, tmpdir):
    ret = script_runner.run('python3', 'o2rmeta.py', '-debug', 'extract', 
        '-i', 'extract/tests/minimal',
        '-o', str(tmpdir))
    assert ret.success, "process should return success"
    assert "http disabled" not in ret.stdout, "should not log staying offline"
    assert ret.stderr == '', "stderr should be empty"

    metadata = json.load(open(os.path.join(str(tmpdir), 'metadata_raw.json')))
    assert "orcid" in metadata['author'][0], "should have orcid entry in authors"
