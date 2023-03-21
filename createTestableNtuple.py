#!/usr/bin/env python3
#Script designed to run a relval or relval like sample
#with a phase 2 trigger command, 
#under both old and new PR repositories

import argparse
import subprocess
from checkPRTestCompiles import checkPRCompiles

def createNtuple(location, command):
    #First things first, we should make sure we have compiled any changes here
    compilationProcess = checkPRCompiles(testRepo=location)
    if compilationProcess.returncode != 0:
        print(f'Compilation of repository failed!')
        print(f'Unable to create ntuple in directory: {location}')
        exit(1)
    
    #now we need to run our cmsDriver command.
    cmsDriverProcess = subprocess.run(
        [command],
        shell=True,
        stderr=subprocess.PIPE,
    )
    if cmsDriverProcess.returncode != 0:
        print("Failed to build ntuple")
        print(f"stderr:{cmsDriverProcess.stderr.decode()}")
        print(f"Return code: {cmsDriverProcess.returncode}")
    
    return cmsDriverProcess


def main(args):
    runNtuplesCommand = './runCmsDriverNtuples.sh'
    locations = (f'{args.location}/old/', f'{args.location}/new/')
    for location in locations:
        cmsDriverCommand = runNtuplesCommand + f' {location}/src/'
        createNtuple(location, command=cmsDriverCommand)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Creates a test ntuple with L1 Content')

    parser.add_argument(
        '-l',
        '--location',
        required=True,
        nargs='?',
        help='Location of the PR test repository'
    )
    """ parser.add_argument(
        '-p',
        '--prURL',
        required=True,
        nargs='?',
        help='PR thread to report to'
    ) """
    parser.add_argument(
        '-d',
        '--dryRun',
        action='store_true',
        help=''
    )

    args = parser.parse_args()
    main(args)