import argparse
import subprocess

from core.tokenHolder import tokenHolder
from core.gitHubRequests import gitHubRequester

def runCommand(theCommand, dryRun):
    if dryRun:
        print(f'\n{theCommand}\n')
        return None
    else:
        theProcess = subprocess.run(
            [theCommand],
            shell=True,
            stderr=subprocess.PIPE
        )
        return theProcess

def main(args):
    theTokenHolder = tokenHolder()
    theGitHubRequester = gitHubRequester(theTokenHolder)

    unitTestCommand = f'python3 checkUnitTests.py -l {args.location} -p {args.prURL}'
    unitTestProcess = runCommand(unitTestCommand, args.dryRun)

    if not (unitTestProcess == None or unitTestProcess.returncode == 0):
        return unitTestProcess.returncode
    
    testNtupleCreationCommand = f'python3 createTestableNtuple.py -l {args.location}'
    testNtupleProcess = runCommand(testNtupleCreationCommand, args.dryRun)

    if not(testNtupleProcess == None or testNtupleProcess.returncode == 0):
        return testNtupleProcess.returncode
    
    ntupleContentCommand = f'python3 checkNtupleContents.py -l {args.location} -p {args.prURL}'
    ntupleContentProcess = runCommand(ntupleContentCommand, args.dryRun)

    if not(ntupleContentProcess == None or ntupleContentProcess.returncode == 0):
        return ntupleContentProcess.returncode
    
    return 0

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Runs the advanced tests for a PR')

    parser.add_argument(
        '-l',
        '--location',
        required=True,
        nargs='?',
        help='location to perform this test'
    )
    parser.add_argument(
        '-p',
        '--prURL',
        required=True,
        nargs='?',
        help='URL of the PR to do tests on',
    )
    parser.add_argument(
        '-d',
        '--dryRun',
        action='store_true',
        help='Don\'t perform any actions. Just print the commands that would be run'
    )

    args = parser.parse_args()
    exitCode = main(args)
    exit(exitCode)