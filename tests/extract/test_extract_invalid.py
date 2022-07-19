# pylint: skip-file
import os
import json

def test_invalid_compendium(script_runner, tmpdir):
    ret = script_runner.run('o2r-meta', '-debug', 'extract', 
        '-i', 'extract/compendium_invalid',
        '-o', str(tmpdir),
        '-xo', '-m')
    print(ret.stdout)
    print(ret.stderr)

    assert ret.success, "process should return success"
    assert ret.stderr == '', "stderr should be empty"
    
    metadata = json.load(open(os.path.join(str(tmpdir), 'metadata_raw.json')))
    assert metadata['displayfile'] is None, "missing displayfile should be none"
    assert metadata['mainfile'] is None, "missing mainfile should be none"
    assert metadata['displayfile'] != "", "missing displayfile should be none not empty string"
    assert metadata['mainfile'] != "", "missing mainfile should be none not empty string"

def test_invalid_compendium_basedir(script_runner, tmpdir):
    ret = script_runner.run('o2r-meta', '-debug', 'extract', 
        '-i', 'extract/compendium_invalid',
        '-b', 'extract/compendium_invalid',
        '-o', str(tmpdir),
        '-xo', '-m')
    print(ret.stdout)
    print(ret.stderr)

    assert ret.success, "process should return success"
    assert ret.stderr == '', "stderr should be empty"
    
    metadata = json.load(open(os.path.join(str(tmpdir), 'metadata_raw.json')))
    assert metadata['displayfile'] is None, "missing displayfile should be none"
    assert metadata['mainfile'] is None, "missing mainfile should be none"
    assert metadata['displayfile'] != "", "missing displayfile should be none not empty string"
    assert metadata['mainfile'] != "", "missing mainfile should be none not empty string"
