# pylint: skip-file
import os
import json
import subprocess
import random
import pytest

global processes
processes = []

mappings = ['/test/broker/mappings/zenodo-map.json',
    '/test/broker/mappings/b2share-map.json',
    #'/test/broker/mappings/o2r-map.json',
    '/test/broker/mappings/zenodo_sandbox-map.json']

# Don't forget to rebuild the image!
# TEST_RACE=yes pytest -vvvvvvv -s broker/tests/test_broker_race.py
# use docker stats to observe progress

def start_process(script_runner, tmpdir, number):
    #print(''.join(('Starting: ', str(number))))   
    process = subprocess.Popen(['docker', 'run', '--rm', '-it',
        '--cpus=0.01', '--cpuset-cpus=0', # slow down containers so more run at the same time, increasing the chance of a race condition for the file package_slip.json
        '-v', os.getcwd() + ':/test',
        '-v', str(tmpdir) + ':' + str(tmpdir),
        'meta', # image name
        '-debug', 'broker',
        '-m', random.choice(mappings),
        '-i', '/test/broker/tests/questiondriven/metadata_raw.json',
        '-o', str(tmpdir)], stdout=subprocess.PIPE)
    processes.append(process)

@pytest.mark.skipif(os.environ.get('TEST_RACE', 'no') == 'no', reason = 'requires Docker and for specific use case, see #104, which does not always happen')
def test_race(script_runner, tmpdir):
    builder = subprocess.Popen(['docker', 'build', '--tag', 'meta', '.'], stdout=subprocess.PIPE)
    builder.wait()

    num_procs = 99
    for i in range(0, num_procs):
        start_process(script_runner, tmpdir, i)

    for i in range(0, num_procs):
        #print(''.join(('Waiting for: ', str(i))))
        #print(''.join(('Checking output of: ', str(i))))
        processes[i].wait()
        
        result = processes[i].communicate()[0]
        #print(''.join(('Result of ', str(i), ': ', str(result))))
        assert "bytes written to" in str(result), "should write output files"
        assert "JSONDecodeError" not in str(result), "should not have errors"
        assert "Expecting value" not in str(result), "should not have errors"
