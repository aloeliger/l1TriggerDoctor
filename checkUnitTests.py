import argparse 
import subprocess
from core.tokenHolder import tokenHolder
from core.gitHubRequests import gitHubRequester
from core.shellCmsenv import cmsenvCommand

def checkUnitTests(location):
    checkCommand = f'{cmsenvCommand} && scram b runtests'
    checkProcess = subprocess.run(
        [checkCommand],
        cwd=f'{args.location}/new/src/',
        shell=True,
        stderr=subprocess.PIPE
    )
    if checkProcess.returncode != 0:
        print('Unit testing failed!')
        print(f'Return code: {checkProcess.returncode}')
        print('stderr:')
        print(f'{checkProcess.stderr.decode()}')
    
    return checkProcess

def reportToPR(testProcess, url, theGitHubRequester, isDryRun):
    message = 'Hello, I\'m triggerDoctor. @aloeliger is testing this script for L1T offline software validation.\n\n'
    if testProcess.returncode != 0:
        message += 'I ran into errors running unit tests for this PR\n'
        message += 'The following is the stderr of the unit testing process:'
        message += f'```\n{testProcess.stderr.decode()}\n```\n'
    else:
        message += 'This PR passes available unit tests!\n'
    message += '|    Info   |     Value    |\n'
    message += '|:---------:|:------------:|\n'
    message +=f'|return code|`{testProcess.returncode}`|\n'
    message +=f'|command|`{testProcess.args[0]}`|'

    if isDryRun:
        print(message)
    else:
        requestJson = theGitHubRequester.createPullOrIssueComment(
            url=url,
            comment=message
        )

def main(args):
    theTokenHolder = tokenHolder()
    theGitHubRequester = gitHubRequester(theTokenHolder)

    testProcess = checkUnitTests(args.location)

    reportToPR(
        testProcess=testProcess,
        url=args.prURL,
        theGitHubRequester=theGitHubRequester,
        isDryRun=args.dryRun
    )

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Runs the relevant unit tests for the PR to check for errors')

    parser.add_argument(
        '-l',
        '--location',
        required=True,
        nargs='?',
        help='Location of the PR test repository'
    )
    parser.add_argument(
        '-p',
        '--prURL',
        required=True,
        nargs='?',
        help='PR thread to take info from and report to'
    )
    parser.add_argument(
        '-d',
        '--dryRun',
        action='store_true',
        help = 'Only print the message, do not report to the thread'
    )

    args = parser.parse_args()
    main(args)