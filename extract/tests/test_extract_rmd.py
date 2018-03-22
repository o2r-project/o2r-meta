# pylint: skip-file
import os
import json

def test_rmd(script_runner, tmpdir):
    ret = script_runner.run('python3', 'o2rmeta.py', '-debug', 'extract', 
        '-i', 'extract/tests/spacetime',
        '-o', str(tmpdir),
        '-b', 'extract/tests/spacetime',
        '-xo', '-m')
    print(ret.stdout)
    print(ret.stderr)

    assert ret.success, "process should return success"
    assert ret.stderr == '', "stderr should be empty"
    
    metadata = json.load(open(os.path.join(str(tmpdir), 'metadata_raw.json')))
    #metadata_base = json.load(open('validate/tests/spacetime.json'))
    
    assert "Spatio-Temporal Data in R" in metadata['title']
    assert len(metadata['author']) == 1, "found one author"
    assert "classes and methods designed to deal with" in metadata['description'] 
    assert metadata['mainfile_candidates'] == ["main.Rmd"]

    assert len(metadata['depends']) > 0, "found dependencies"
    packageSystems = [dep['packageSystem'] for dep in metadata['depends']]
    assert packageSystems == ["https://cloud.r-project.org/"] * len(metadata['depends']), "all dependencies come from cloud.r-project.org"
    categories = set([cat['category'] for cat in metadata['depends']])
    assert {"geo sciences,CRAN Top100", "geo sciences", None} == categories, "found all categories"
    