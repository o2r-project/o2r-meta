# pylint: skip-file
import os
import json

def test_compendium(script_runner, tmpdir):
    ret = script_runner.run('python3', 'o2rmeta.py', '-debug', 'extract', 
        '-i', 'extract/tests/compendium',
        '-o', str(tmpdir),
        '-xo', '-m')
    print(ret.stdout)
    print(ret.stderr)

    assert ret.success, "process should return success"
    assert ret.stderr == '', "stderr should be empty"
    assert "total files processed: 1" in ret.stdout, "should process 1 file"
    
    metadata = json.load(open(os.path.join(str(tmpdir), 'metadata_raw.json')))
    assert metadata['displayfile'] == "paper.html"
    assert metadata['mainfile'] == "paper.rmd"

def test_compendium_basedir(script_runner, tmpdir):
    ret = script_runner.run('python3', 'o2rmeta.py', '-debug', 'extract', 
        '-i', 'extract/tests/compendium',
        '-o', str(tmpdir),
        '-b', 'extract/tests/compendium',
        '-xo', '-m')
    print(ret.stdout)
    print(ret.stderr)

    assert ret.success, "process should return success"
    assert ret.stderr == '', "stderr should be empty"
    assert "total files processed: 1" in ret.stdout, "should process 1 file"
    
    metadata = json.load(open(os.path.join(str(tmpdir), 'metadata_raw.json')))
    assert metadata['displayfile'] == "paper.html"
    assert metadata['mainfile'] == "paper.rmd"

def test_minimal(script_runner, tmpdir):
    ret = script_runner.run('python3', 'o2rmeta.py', '-debug', 'extract', 
        '-i', 'extract/tests/minimal',
        '-o', str(tmpdir),
        '-xo', '-m')
    print(ret.stdout)
    print(ret.stderr)

    assert ret.success, "process should return success"
    assert ret.stderr == '', "stderr should be empty"
    assert "total files processed: 2" in ret.stdout, "should process 2 files"
    
    metadata = json.load(open(os.path.join(str(tmpdir), 'metadata_raw.json')))
    assert metadata['displayfile'] == "extract/tests/minimal/display.html"
    assert metadata['mainfile'] == "extract/tests/minimal/main.Rmd"
    
def test_minimal_basedir(script_runner, tmpdir):
    ret = script_runner.run('python3', 'o2rmeta.py', '-debug', 'extract', 
        '-i', 'extract/tests/minimal',
        '-o', str(tmpdir),
        '-b', 'extract/tests/minimal',
        '-xo', '-m')
    print(ret.stdout)
    print(ret.stderr)

    assert ret.success, "process should return success"
    assert ret.stderr == '', "stderr should be empty"
    assert "total files processed: 2" in ret.stdout, "should process 2 files"
    
    metadata = json.load(open(os.path.join(str(tmpdir), 'metadata_raw.json')))
    assert metadata['displayfile'] == "display.html", "displayfile path should be relative to basedir"
    assert metadata['mainfile'] == "main.Rmd", "mainfile path should be relative to basedir"
