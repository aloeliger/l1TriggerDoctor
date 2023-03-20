import argparse
import subprocess
from subprocess import CalledProcessError

from core.tokenHolder import tokenHolder
from core.gitHubRequests import gitHubRequester

def runCommand(theCommand, dryRun):
    if dryRun:
        print(f'\n{theCommand}\n')
    else:
        try:
            theProcess = subprocess.run(
                [theCommand],
                shell=True,
                stderr=subprocess.PIPE,
                check=True,
            )
        except CalledProcessError as err:
            print(f'CalledProcessError with commmand: {theCommand}')
            print(f'stderr:\n{theProcess.stderr.decode()}')
            raise

def main(args):
    theTokenHolder = tokenHolder()
    theGitHubRequester = gitHubRequester(theTokenHolder)
    #Get the PR info
    prJSON = theGitHubRequester.getPullRequestInformation(args.prURL)
    prNum = prJSON['number']
    #Create a test setup
    testSetupCommand = f'python3 createPRTestSetup.py -r {args.release} -p {args.prURL} -l {args.location}'
    runCommand(testSetupCommand, args.dryRun)
    #Check if the PR compiles
    compilationCommand = f'python3 checkPRTestCompiles.py -l {args.location}/pr_{prNum}/new/ -p {args.prURL}'
    runCommand(compilationCommand, args.dryRun)
    #Check code checks
    codeCheckCommand = f'python3 checkPRTestCodeChecks.py -l {args.location}/pr_{prNum}/new/ -p {args.prURL}'
    runCommand(codeCheckCommand, args.dryRun)
    #Check if the PR is properly formatted
    formatCommand = f'python3 checkPRTestCodeFormat.py -l {args.location}/pr_{prNum}/new/ -p {args.prURL}'
    runCommand(formatCommand, args.dryRun)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Creates a test set-up, and runs compilation and format checks for a given PR')

    parser.add_argument(
        '-r',
        '--release',
        required=True,
        nargs='?',
        help='CMSSW release to perform the tests in',
    )
    parser.add_argument(
        '-p',
        '--prURL',
        required=True,
        nargs='?',
        help='URL of the PR to do tests on',
    )
    parser.add_argument(
        '-l',
        '--location',
        required=True,
        nargs='?',
        help='location to perform the test',
    )

    parser.add_argument(
        '-d',
        '--dryRun',
        action='store_true',
        help='Don\'t perform any actions. Just print the commands that would be run'
    )

    args = parser.parse_args()
    main(args)