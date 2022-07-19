import json
import os
import pytest

tolerance = 1e-3


def test_geospatial(script_runner, tmpdir):
    ret = script_runner.run('o2r-meta', 'extract',
                            '-i', 'extract/geojson',
                            '-o', str(tmpdir),
                            '-xo', '-m')
    assert ret.success, "process should return success"
    assert ret.stderr == '', "stderr should be empty"
    metadata = json.load(open(os.path.join(str(tmpdir), 'metadata_raw.json')))
    assert metadata["spatial"]["union"] == pytest.approx([7.60614, 50.07708, 12.04290, 51.96587], abs=tolerance)
