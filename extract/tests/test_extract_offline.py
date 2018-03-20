# pylint: skip-file
import pytest

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
    assert "http disabled" not in ret.stdout, "should no log staying offline"
    assert "downloading current erc spec" in ret.stdout, "should log downloading spec"
    assert ret.stderr == '', "stderr should be empty"
