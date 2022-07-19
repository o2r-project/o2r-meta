# pylint: skip-file
import os
import json

def test_package_slip(script_runner, tmpdir):
    output_file = os.path.join(str(tmpdir), 'package_slip.json')

    ret = script_runner.run('o2r-meta',
        '-debug',
        'broker',
        '-m', 'broker/mappings/zenodo-map.json',
        '-i', 'broker/questiondriven/metadata_raw.json',
        '-o', str(tmpdir))
    
    assert ret.success, "process should return success"
    assert ret.stderr == '', "stderr should be empty"
    
    slipdata = json.load(open(output_file))
    assert len(slipdata['standards_used']) == 1
    assert list(slipdata['standards_used'][0].keys()) == ['zenodo']
    assert slipdata['standards_used'][0]['zenodo']['version'] == "1"
    assert slipdata['standards_used'][0]['zenodo']['name'] == "zenodo"

    ret = script_runner.run('o2r-meta',
        '-debug',
        'broker',
        '-m', 'broker/mappings/o2r-map.json',
        '-i', 'broker/questiondriven/metadata_raw.json',
        '-o', str(tmpdir))
    
    assert ret.success, "process should return success"
    assert ret.stderr == '', "stderr should be empty"
    
    slipdata = json.load(open(output_file))
    assert len(slipdata['standards_used']) == 2
    assert list(slipdata['standards_used'][1].keys()) == ['o2r']
    assert slipdata['standards_used'][1]['o2r']['version'] == "1"
    assert slipdata['standards_used'][1]['o2r']['name'] == "o2r"
