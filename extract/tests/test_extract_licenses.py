# pylint: skip-file
import os
import json

def test_rmd_header(script_runner, tmpdir):    
    ret = script_runner.run('python3', 'o2rmeta.py', 'extract', 
        '-i', 'extract/tests/licenses/rmd',
        '-o', str(tmpdir),
        '-xo', '-m')
    assert ret.success, "process should return success"
    assert ret.stderr == '', "stderr should be empty"
    
    metadata = json.load(open(os.path.join(str(tmpdir), 'metadata_raw.json')))
    assert "title" in metadata, "should have title entry"
    assert "container ships" in metadata['title']
    assert "licenses" in metadata, "should have licenses entry"
    assert len(metadata['licenses']) == 5, "should have 5 licenses"
    assert metadata['licenses']['code'] == "Apache-2.0"
    assert metadata['licenses']['data'] == "CC0-1.0"
    assert metadata['licenses']['text'] == "ODbL-1.0"
    assert metadata['licenses']['ui_bindings'] == "good boy license"
    assert metadata['licenses']['metadata'] == "license-md.txt"

def test_rmd_header_incomplete(script_runner, tmpdir):    
    ret = script_runner.run('python3', 'o2rmeta.py', 'extract', 
        '-i', 'extract/tests/licenses/rmd_incomplete',
        '-o', str(tmpdir),
        '-xo', '-m')
    assert ret.success, "process should return success"
    assert ret.stderr == '', "stderr should be empty"
    
    metadata = json.load(open(os.path.join(str(tmpdir), 'metadata_raw.json')))
    assert "licenses" in metadata, "should have licenses entry"
    assert len(metadata['licenses']) == 2, "should have only 2 licenses"
    assert "data" not in metadata['licenses'], "should not have license entry for data"
    assert "ui_bindings" not in metadata['licenses'], "should not have license entry for ui_bindings"
    assert "text" not in metadata['licenses'], "should not have license entry for text"
    assert metadata['licenses']['code'] == "Apache-2.0"
    assert metadata['licenses']['metadata'] == "CC0-1.0"
