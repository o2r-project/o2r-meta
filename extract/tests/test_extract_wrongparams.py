# pylint: skip-file
import os
import json

def test_rmd(script_runner, tmpdir):
    ret = script_runner.run('python3', 'o2rmeta.py', 'extract', 
        '-i', 'dir/does/not/exist',
        '-o', str(tmpdir),
        '-xo', '-m')
    print(ret.stdout)
    print(ret.stderr)
    assert not ret.success, "process should not return success"
    assert "dir/does/not/exist" in ret.stderr, "stderr should mention wrong path"
