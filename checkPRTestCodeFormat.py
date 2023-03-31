#Script to check if a PR has code formatting issues
#It will report back to the thread the files it has found that do not meet code formatting requirements
import argparse
import subprocess
from core.tokenHolder import tokenHolder
from core.gitHubRequests import gitHubRequester
from subprocess import CalledProcessError


def checkCodeFormatting(testRepo):
    command = 'cmsenv && scram b -k -j 8 code-format-all'
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

def reportToPR(diffProcess, url, theGitHubRequester, isDryRun):
    message = 'Hello, I\'m triggerDoctor. @aloeliger is testing this script for L1T offline software validation.\n\n'
    diffFiles = diffProcess.stdout.decode().split('\n')
    diffFiles.remove('')
    if len(diffFiles) != 0:
        message += f'I found {len(diffFiles)} files that did not meet formatting requirements:\n'
        for fileName in diffFiles:
            message+= f' - {fileName}\n'
        message += '\nPlease run `scram b code-format` to auto-apply code formatting\n'
    else:
        #print('I found no files with code format issues!')
        message += 'I found no files with code format issues!\n'
    
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

    diffProcess = checkCodeFormatting(args.location)

    reportToPR(
        diffProcess=diffProcess,
        url=args.prURL,
        theGitHubRequester=theGitHubRequester,
        isDryRun=args.dryRun
    )


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description = 'Checks whether any code formatting needs to be applied to a create PR repository and will report to a github thread about it')

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
        help='Only print the message, do not report to the thread'
    )

    args = parser.parse_args()
    main(args)