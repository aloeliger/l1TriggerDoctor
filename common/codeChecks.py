#!/usr/bin/env python3
#some common elements to code formatting and code checking scripts

import subprocess
from subprocess import CalledProcessError

def checkCode(testRepo, command):
    try:
        checkProcess = subprocess.run(
            [command],
            shell=True,
            cwd = testRepo+'/src/',
            stderr=subprocess.PIPE,
        )
    except CalledProcessError as err:
        print('Failed to run a code check:')
        print(f'command: {command}')
        print(f'stderr: {checkProcess.stderr.decode()}')
        print(f'returncode: {checkProcess.returncode}')
        raise
    
    #Check the diffs
    diffCommand = 'git diff --name-only'
    try:
        diffProcess = subprocess.run(
            [diffCommand],
            shell=True,
            cwd=testRepo+'/src/',
            stderr=subprocess.PIPE,
            stdout=subprocess.PIPE,
        )
    except CalledProcessError as err:
        print('git diff failed!')
        print(f'stderr:\n{diffProcess.stderr.decode()}')
        print(f'returncoded:\n{diffProcess.returncode}')
        raise

    assert(diffProcess.returncode==0), 'diff returned non-0 return! Results likely invalid!'

    #Let's set the repository back to the way we found it
    resetCommand = 'git checkout *'
    subprocess.run(
        [resetCommand],
        shell=True,
        cwd=testRepo+'/src/',
    )

    return diffProcess