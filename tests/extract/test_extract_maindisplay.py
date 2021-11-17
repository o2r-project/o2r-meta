# pylint: skip-file
import os
import json

def test_compendium(script_runner, tmpdir):
    ret = script_runner.run('o2r-meta', '-debug', 'extract', 
        '-i', 'extract/compendium',
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
    ret = script_runner.run('o2r-meta', '-debug', 'extract', 
        '-i', 'extract/compendium',
        '-o', str(tmpdir),
        '-b', 'extract/compendium',
        '-xo', '-m')
    print(ret.stdout)
    print(ret.stderr)

    assert ret.success, "process should return success"
    assert ret.stderr == '', "stderr shosuld be empty"
    assert "total files processed: 1" in ret.stdout, "should process 1 file"
    
    metadata = json.load(open(os.path.join(str(tmpdir), 'metadata_raw.json')))
    assert metadata['displayfile'] == "paper.html"
    assert metadata['mainfile'] == "paper.rmd"

def test_minimal(script_runner, tmpdir):
    ret = script_runner.run('o2r-meta', '-debug', 'extract', 
        '-i', 'extract/minimal',
        '-o', str(tmpdir),
        '-xo', '-m')
    print(ret.stdout)
    print(ret.stderr)

    assert ret.success, "process should return success"
    assert ret.stderr == '', "stderr should be empty"
    assert "total files processed: 2" in ret.stdout, "should process 2 files"
    
    metadata = json.load(open(os.path.join(str(tmpdir), 'metadata_raw.json')))
    assert metadata['displayfile'] == "extract/minimal/display.html"
    assert metadata['mainfile'] == "extract/minimal/main.Rmd"
    
def test_minimal_basedir(script_runner, tmpdir):
    ret = script_runner.run('o2r-meta', '-debug', 'extract', 
        '-i', 'extract/minimal',
        '-o', str(tmpdir),
        '-b', 'extract/minimal',
        '-xo', '-m')
    print(ret.stdout)
    print(ret.stderr)

    assert ret.success, "process should return success"
    assert ret.stderr == '', "stderr should be empty"
    assert "total files processed: 2" in ret.stdout, "should process 2 files"
    
    metadata = json.load(open(os.path.join(str(tmpdir), 'metadata_raw.json')))
    assert metadata['displayfile'] == "display.html", "displayfile path should be relative to basedir"
    assert metadata['mainfile'] == "main.Rmd", "mainfile path should be relative to basedir"

def test_best_displayfile_candidate(script_runner, tmpdir):
    ret = script_runner.run('o2r-meta', '-debug', 'extract', 
        '-i', 'extract/displayfiles/best_by_name',
        '-o', str(tmpdir),
        '-b', 'extract/displayfiles/best_by_name',
        '-xo', '-m')
    print(ret.stdout)
    print(ret.stderr)

    assert ret.success, "process should return success"
    assert ret.stderr == '', "stderr should be empty"
    
    metadata = json.load(open(os.path.join(str(tmpdir), 'metadata_raw.json')))
    assert metadata['displayfile'] == "display.html", "best matching file should be displayfile"
    assert len(metadata['displayfile_candidates']) == 7, "should have 7 candidates"
    assert "display.pdf" not in metadata['displayfile_candidates'], "should not list pdf as displayfile candidate"
    assert metadata['displayfile_candidates'][0] == "display.html", "best matching displayfile should be first in candidate list"

def test_best_mainfile_candidate(script_runner, tmpdir):
    ret = script_runner.run('o2r-meta', '-debug', 'extract', 
        '-i', 'extract/displayfiles/best_by_name',
        '-o', str(tmpdir),
        '-b', 'extract/displayfiles/best_by_name',
        '-xo', '-m')
    print(ret.stdout)
    print(ret.stderr)

    assert ret.success, "process should return success"
    assert ret.stderr == '', "stderr should be empty"
    
    metadata = json.load(open(os.path.join(str(tmpdir), 'metadata_raw.json')))
    assert metadata['mainfile'] == "main.Rmd", "best matching file should be displayfile"
    assert len(metadata['mainfile_candidates']) == 4, "should have 4 candidates"
    assert metadata['mainfile_candidates'][0] == "main.Rmd", "best matching displayfile should be first in candidate list"
    
