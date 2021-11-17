# pylint: skip-file
import pytest

# more complex test including extraction, brokering and validation
def test_fullstack_minimal_offline(script_runner, tmpdir):
    ret_extract = script_runner.run('o2r-meta', 'extract',
        '-i', 'extract/minimal',
        '-o', str(tmpdir),
        '-xo')
    assert ret_extract.success, "extract process should return success"
    ret_broker = script_runner.run('o2r-meta',
        '-debug',
        'broker',
        '-m', 'broker/mappings/o2r-map.json',
        '-i', str(tmpdir) + '/metadata_raw.json',
        '-o', str(tmpdir))
    assert ret_broker.success, "broker process should return success"

    ret = script_runner.run('o2r-meta', '-debug', 'validate',
        '-s', 'schema/json/o2r-meta-schema.json',
        '-c', str(tmpdir) + '/metadata_o2r_1.json')
    print(ret.stdout)
    print(ret.stderr)

    assert ret.success, "process should return success"
    assert ret.stderr == '', "stderr should be empty"
    assert "checking metadata_o2r_1.json" in ret.stdout, "should log validated file"
    assert "invalid" not in ret.stdout, "should result in valid"

def test_fullstack_minimal_online(script_runner, tmpdir):
    ret_extract = script_runner.run('o2r-meta', 'extract',
        '-i', 'extract/minimal',
        '-o', str(tmpdir))
    assert ret_extract.success, "extract process should return success"
    ret_broker = script_runner.run('o2r-meta','-debug',
        'broker',
        '-m', 'broker/mappings/o2r-map.json',
        '-i', str(tmpdir) + '/metadata_raw.json',
        '-o', str(tmpdir))
    assert ret_broker.success, "broker process should return success"

    ret = script_runner.run('o2r-meta', '-debug', 'validate',
        '-s', 'schema/json/o2r-meta-schema.json',
        '-c', str(tmpdir) + '/metadata_o2r_1.json')
    print(ret.stdout)
    print(ret.stderr)

    assert ret.success, "process should return success"
    assert ret.stderr == '', "stderr should be empty"
    assert "checking metadata_o2r_1.json" in ret.stdout, "should log validated file"
    assert "invalid" not in ret.stdout, "should result in valid"
