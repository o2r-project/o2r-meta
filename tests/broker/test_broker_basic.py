# pylint: skip-file
import os
import json

def test_zenodo(script_runner, tmpdir):
    ret = script_runner.run('o2r-meta',
        '-debug',
        'broker',
        '-m', 'broker/mappings/zenodo-map.json',
        '-i', 'broker/questiondriven/metadata_raw.json',
        '-o', str(tmpdir))
    
    assert ret.success, "process should return success"
    assert ret.stderr == '', "stderr should be empty"
    assert "processing element <identifier>" in ret.stdout, " processed elements should be logged"
    assert "processing element <spatial>" not in ret.stdout, " not processed elements should not be logged"
    output_file = os.path.join(str(tmpdir), 'metadata_zenodo_1.json')
    assert "bytes written to " + output_file in ret.stdout, " output file should be logged"
    
    metadata = json.load(open(output_file))
    assert metadata['communities'][0]['identifier'] == "o2r"
    assert metadata['keywords'] == []
    assert metadata['title'] == "A question driven socio-hydrological modeling process"
    assert metadata['upload_type'] == "publication"
    assert metadata['publication_type'] == "other"

def test_o2r(script_runner, tmpdir):
    ret = script_runner.run('o2r-meta',
        '-debug',
        'broker',
        '-m', 'broker/mappings/o2r-map.json',
        '-i', 'broker/questiondriven/metadata_raw.json',
        '-o', str(tmpdir))
    
    assert ret.success, "process should return success"
    assert ret.stderr == '', "stderr should be empty"
    assert "processing element <spatial>" in ret.stdout, " processed elements should be logged"
    assert "processing element <codefiles>" in ret.stdout, " processed elements should be logged"
    output_file = os.path.join(str(tmpdir), 'metadata_o2r_1.json')
    assert "bytes written to " + output_file in ret.stdout, " output file should be logged"
    
    metadata = json.load(open(output_file))
    assert metadata['communities'][0]['identifier'] == "o2r"
    assert len(metadata['creators']) == 3, " all authors are mapped to creators"
    assert len(metadata['codefiles']) == 6, " codefiles mapped"
    assert len(metadata['inputfiles']) == 1, " inputfiles mapped"
    assert metadata['displayfile'] == "display.html", " displayfile mapped"
    assert metadata['mainfile'] == "main.Rmd", " mainfile mapped"
    assert metadata['title'] == "A question driven socio-hydrological modeling process"
    assert metadata['upload_type'] == "publication"
    assert metadata['publication_type'] == "other"
    assert metadata['identifier']['doi'] == "doi:10.5194/hess-20-73-2016"
