#!/usr/bin/env python3
#Script to check if a PR has code check issues
#It will report back to the thread the files it has found that have code check issues
import argparse
import subprocess
from core.tokenHolder import tokenHolder
from core.gitHubRequests import gitHubRequester
from subprocess import CalledProcessError
from common.codeChecks import checkCode

def checkCodeChecks(testRepo):
    checkCommand = 'cmsenv && scram b -k -j 8 code-checks'
    diffProcess = checkCode(testRepo, checkCommand)
    return diffProcess

def reportToPR(diffProcess, url, theGitHubRequester, isDryRun):
    message = 'Hello, I\'m triggerDoctor. @aloeliger is testing this script for L1T offline software validation.\n\n'
    diffFiles = diffProcess.stdout.decode().split('\n')
    diffFiles.remove('')
    if len(diffFiles) != 0:
        message += f'I found {len(diffFiles)} files that did not pass code checks:\n'
        for fileName in diffFiles:
            message+= f' - {fileName}\n'
        message += '\nPlease run `scram b code-checks` to auto-apply code formatting\n'
    else:
        #print('I found no files with code format issues!')
        message += 'I found no files with code check issues!'
    
    if isDryRun:
        print(message)
    else:
        requestJson = theGitHubRequester.createPullOrIssueComment(
            url=url,
            comment = message
        )

def main(args):
    theTokenHolder = tokenHolder()
    theGitHubRequester = gitHubRequester(theTokenHolder)

    diffProcess = checkCodeChecks(args.location)

    reportToPR(
        diffProcess=diffProcess,
        url=args.prURL,
        theGitHubRequester=theGitHubRequester,
        isDryRun=args.dryRun
    )

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description = 'Check whether any code checking needs to be applied to a PR')

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
        help='PR thread to take info from, and report to'
    )
    parser.add_argument(
        '-d',
        '--dryRun',
        action='store_true',
        help = 'Only print the message, do not report to the thread'
    )

    args = parser.parse_args()
    main(args)