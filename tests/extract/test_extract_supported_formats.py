def test_listing_of_supported_formats(script_runner):
    ret = script_runner.run('o2r-meta', 'extract', '-f')
    assert ret.success, "process should return success"
    assert "list of supported formats" in ret.stdout
    assert ".html" in ret.stdout, "html should be listed"
    assert ".rmd" in ret.stdout, "rmd should be listed"
    assert ".r" in ret.stdout, "r should be listed"
    assert ret.stderr == '', "stderr should be empty"

def test_logging_of_skipped_files(script_runner, tmpdir):
    ret = script_runner.run('o2r-meta', 'extract', 
        '-i', 'extract/compendium',
        '-o', str(tmpdir),
        '-xo', '-m')
    print(ret.stdout)
    print(ret.stderr)

    assert ret.success, "process should return success"
    #assert ret.stderr == '', "stderr should be empty"

    assert "extracted from: extract/compendium/erc.yml" in ret.stdout, " extracted files should be listed"
    assert "total files processed: 1" in ret.stdout, "should process 1 file"
    assert "total extraction errors: 0" in ret.stdout, "should have 0 extraction errors"
    assert "total skipped files: 1" in ret.stdout, "should skip 1 files"
