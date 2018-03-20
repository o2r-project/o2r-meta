def test_listing_of_supported_formats(script_runner):
    ret = script_runner.run('python3', 'o2rmeta.py', 'extract', '-f')
    assert ret.success, "process should return success"
    assert "list of supported formats" in ret.stdout
    assert ".html" in ret.stdout, "html should be listed"
    assert ".rmd" in ret.stdout, "rmd should be listed"
    assert ".r" in ret.stdout, "r should be listed"
    assert ret.stderr == '', "stderr should be empty"