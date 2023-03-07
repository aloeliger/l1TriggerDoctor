#Script to check if a PR compiles.
#It will report back to the thread if the PR is found to compile
import argparse
import subprocess
from core.tokenHolder import tokenHolder
from core.gitHubRequests import gitHubRequester

def checkPRCompiles(testRepo):
    compilationCommand = 'cmsenv && scram b -j 8'

    compilationProcess = subprocess.run(
        [compilationCommand],
        shell=True,
        cwd=testRepo+'/src/',
        stderr=subprocess.PIPE
    )

    if compilationProcess.returncode != 0:
        print('Failed to compile!')
        print('stderr:')
        print(compilationProcess.stderr.decode())

    return compilationProcess

def reportToPR(compilationProcess, url, theGitHubRequester, isDryRun):
    message = 'Hello, I\'m triggerDoctor. @aloeliger is testing this script for L1T offline software validation.\n\n'
    if compilationProcess.returncode == 0:
        message+='Attempts to compile this PR succeeded!\n\n'
    else:
        message+='Attempts to compile this PR failed.\n\n'
        message+='The following is the stderr of the compilation attempt:\n'
        message+=f'```\n{compilationProcess.stderr.decode()}\n```\n'
    message += '|    Info   |     Value    |\n'
    message += '|:---------:|:------------:|\n'
    message +=f'|return code|`{compilationProcess.returncode}`|\n'
    message +=f'|command|`{compilationProcess.args[0]}`|'

    if isDryRun:
        print(message)
    else:
        requestJson = theGitHubRequester.createPullOrIssueComment(
            url=url,
            comment=message,
        )

def main(args):
    theTokenHolder = tokenHolder()
    theGitHubRequester = gitHubRequester(theTokenHolder)
    
    compilationProcess = checkPRCompiles(args.location)

    reportToPR(
        compilationProcess = compilationProcess,
        url = args.prURL,
        theGitHubRequester = theGitHubRequester,
        isDryRun = args.dryRun
    )

    return compilationProcess.returncode

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description = 'Checks the SCRAM-ability of a created PR repository, and will report back')

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
        help='PR thread to report to'
    )
    parser.add_argument(
        '-d',
        '--dryRun',
        action='store_true',
        help='Attempt to compile, but only print the statement, do not report to the thread'
    )

    args = parser.parse_args()
    
    exitCode = main(args)
