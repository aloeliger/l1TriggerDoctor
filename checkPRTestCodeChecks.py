#!/usr/bin/env python3
#Script to check if a PR has code check issues
#It will report back to the thread the files it has found that have code check issues
import argparse
import subprocess
from core.tokenHolder import tokenHolder
from core.gitHubRequests import gitHubRequester
from subprocess import CalledProcessError

import re

def checkCodeChecks(testRepo):
    checkCommand = 'cmsenv && scram b -k -j 8 code-checks && scram b -k -j 8 code-checks'
    try:
        checkProcess = subprocess.run(
            [checkCommand],
            shell=True,
            cwd = testRepo+'/src/',
            stderr=subprocess.PIPE,
            stdout=subprocess.PIPE,
        )
    except CalledProcessError as err:
        print('Failed to run a code checks:')
        print(f'command: {checkCommand}')
        print(f'stderr: {checkProcess.stderr.decode()}')
        print(f'returncode: {checkProcess.returncode}')
        raise
    
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
        print('git diff failed')
        print(f'stderr:\n{diffProcess.stderr.decode()}')
        print(f'returncode:\n{diffProcess.returncode}')
        raise

    headerCheckCommand = 'cmsenv && scram b -k -j 8 check-headers'

    try:
        headerProcess = subprocess.run(
            [headerCheckCommand],
            shell=True,
            cwd=testRepo+'/src/',
            stderr=subprocess.PIPE
        )
    except CalledProcessError as err:
        print('Failed to properly check headers')
        print(f'stderr:\n{headerProcess.stderr.decode()}')
        print(f'returncode:\n{headerProcess.returncode}')
    
    return checkProcess, diffProcess, headerProcess

def reportToPR(checkProcess, diffFiles, headerProcess, url, theGitHubRequester, isDryRun):
    message = 'Hello, I\'m triggerDoctor. @aloeliger is testing this script for L1T offline software validation.\n\n'

    if checkProcess.returncode != 0:
        message+='This PR failed the code checks.\n\n'
        #message+='The following is the stderr of the code checks:\n'
        #message+=f'```\n{checkProcess.stderr.decode()}\n```\n'
        errorLineRE='(?<=\n).*[Ee]rror:.*?(?=\n)'
        outErrors = re.findall(errorLineRE, checkProcess.stdout.decode())
        errErrors = re.findall(errorLineRE, checkProcess.stderr.decode())

        """print(outErrors)
        print(outErrors.group(0))
        print(errErrors) """

        if not outErrors and not errErrors:
            message += 'I didn\'t find any errors mentioned explicitly. I\'m sorry. Please run the code checks yourself and try to locate the error.\n'
        else:
            message += 'I found the following lines where an "error" was mentioned, they may help in debugging\n'
            message += '```\n'
            for match in outErrors:
                message+=f'{match}\n'
                message+= '...\n'
            # for match in errErrors:
            #     message+=f'{match}\n'
            #     message+= '-'*30+'\n'
            message += '```\n'
            message += 'Please check and see if these lines help debugging.\n'


        if len(diffFiles) != 0:
            message += f'I found {len(diffFiles)} files that did not pass code checks, but may have automatic fixes:\n'
            for fileName in diffFiles:
                message+= f' - {fileName}\n'
            message += '\nPlease run `scram b code-checks` to auto-apply these code check fixes\n'
    else:
        message += 'I found no issues with the code checks!\n'

    message += '|    Info   |     Value    |\n'
    message += '|:---------:|:------------:|\n'
    message +=f'|return code|`{checkProcess.returncode}`|\n'
    message +=f'|command|`{checkProcess.args[0]}`|\n\n'

    if headerProcess.returncode != 0:
        message += 'I found issues with the headers. These issues likely arise from improper build files.\n\n'
        message += 'The following is the stderr of the header checking:\n'
        message += f'```\n{headerProcess.stderr.decode()}\n```\n'
    
    else:
        message += 'I found no issues with the headers!'

    message += '|    Info   |     Value    |\n'
    message += '|:---------:|:------------:|\n'
    message +=f'|return code|`{headerProcess.returncode}`|\n'
    message +=f'|command|`{headerProcess.args[0]}`|\n\n'

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

    checkProcess, diffProcess, headerProcess = checkCodeChecks(args.location)

    diffFiles = diffProcess.stdout.decode().split('\n')
    diffFiles.remove('')
    #let's make sure to set these files back to the way they used to be
    for fileName in diffFiles:
        resetCommand = f'git checkout {fileName}'
        subprocess.run(
            [resetCommand],
            shell=True,
            cwd=args.location+'/src/'
        )

    reportToPR(
        checkProcess=checkProcess,
        diffFiles=diffFiles,
        headerProcess=headerProcess,
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