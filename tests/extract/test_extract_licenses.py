# pylint: skip-file
import os
import json

def test_rmd_header(script_runner, tmpdir):    
    ret = script_runner.run('o2r-meta', '-debug', 'extract', 
        '-i', 'extract/licenses/rmd',
        '-o', str(tmpdir),
        '-xo', '-m')
    print(ret.stdout)
    print(ret.stderr)

    assert ret.success, "process should return success"
    #assert ret.stderr == '', "stderr should be empty"
    
    metadata = json.load(open(os.path.join(str(tmpdir), 'metadata_raw.json')))
    assert "license" in metadata, "should have license entry"
    assert len(metadata['license']) == 4, "should have 4 licenses"
    assert metadata['license']['code'] == "Apache-2.0"
    assert metadata['license']['data'] == "CC0-1.0"
    assert metadata['license']['text'] == "ODbL-1.0"
    assert metadata['license']['metadata'] == "license-md.txt"

def test_rmd_header_incomplete(script_runner, tmpdir):    
    ret = script_runner.run('o2r-meta', '-debug', 'extract', 
        '-i', 'extract/licenses/rmd_incomplete',
        '-o', str(tmpdir),
        '-xo', '-m')
    print(ret.stdout)
    print(ret.stderr)

    assert ret.success, "process should return success"
    #assert ret.stderr == '', "stderr should be empty"
    
    metadata = json.load(open(os.path.join(str(tmpdir), 'metadata_raw.json')))
    assert "license" in metadata, "should have license entry"
    assert len(metadata['license']) == 2, "should have only 2 license"
    assert "data" not in metadata['license'], "should not have license entry for data"
    assert "text" not in metadata['license'], "should not have license entry for text"
    assert metadata['license']['code'] == "Apache-2.0"
    assert metadata['license']['metadata'] == "CC0-1.0"

def test_erc_yml(script_runner, tmpdir):
    ret = script_runner.run('o2r-meta', '-debug', 'extract', 
        '-i', 'extract/licenses/erc_yml',
        '-o', str(tmpdir),
        '-xo', '-m')
    print(ret.stdout)
    print(ret.stderr)

    assert ret.success, "process should return success"
    assert ret.stderr == '', "stderr should be empty"
    
    metadata = json.load(open(os.path.join(str(tmpdir), 'metadata_raw.json')))
    assert "license" in metadata, "should have license entry"
    assert len(metadata['license']) == 4, "should have 4 licenses"
    assert metadata['license']['code'] == "Apache-2.0"
    assert metadata['license']['data'] == "ODbL-1.0"
    assert metadata['license']['text'] == "CC0-1.0"
    assert metadata['license']['metadata'] == "license-md.txt"

def test_rmd_header_default_license(script_runner, tmpdir):    
    ret = script_runner.run('o2r-meta', '-debug', 'extract', 
        '-i', 'extract/licenses/rmd-default',
        '-o', str(tmpdir),
        '-xo', '-m')
    print(ret.stdout)
    print(ret.stderr)

    assert ret.success, "process should return success"
    assert ret.stderr == '', "stderr should be empty"
    
    metadata = json.load(open(os.path.join(str(tmpdir), 'metadata_raw.json')))
    assert "license" in metadata, "should have license entry"
    assert len(metadata['license']) == 4, "should have 4 licenses"
    assert metadata['license']['metadata'] == "CC-BY-4.0"

def test_cli_define_default_license(script_runner, tmpdir):    
    ret = script_runner.run('o2r-meta', '-debug', 'extract', 
        '-i', 'extract/licenses/rmd-default',
        '-o', str(tmpdir),
        '-lic', 'my own license',
        '-xo', '-m')
    print(ret.stdout)
    print(ret.stderr)

    assert ret.success, "process should return success"
    #assert ret.stderr == '', "stderr should be empty"
    
    metadata = json.load(open(os.path.join(str(tmpdir), 'metadata_raw.json')))
    assert "license" in metadata, "should have license entry"
    assert len(metadata['license']) == 4, "should have 4 licenses"
    assert metadata['license']['metadata'] == "my own license", "should override the hard-coded default"
