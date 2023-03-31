#script to check if a PR introduces new contents to L1 trigger output
import argparse
import subprocess
from core.tokenHolder import tokenHolder
from core.gitHubRequests import gitHubRequester
import re

def dumpEventContent(fileLocation):
    dumpCommand = f'cmsenv && edmDumpEventContent {fileLocation}/test.root'

    dumpProcess = subprocess.run(
        [dumpCommand],
        shell=True,
        cwd=fileLocation,
        stderr=subprocess.PIPE,
        stdout=subprocess.PIPE,
    )
    
    return dumpProcess

def parseEventContent(edmDump):
    parsedContents = []

    edmDump = edmDump.split('\n')
    edmDump.remove('')

    labelLine = edmDump[0]
    labels = re.split('\W+', labelLine)
    labels.remove('')

    contents = edmDump[2:]
    for line in contents:
        lineDict = {}
        splitLine = re.split('"?\s\s+"?', line)
        splitLine=splitLine[:len(splitLine)-1]
        for elementNum, element in enumerate(splitLine):
            lineDict[labels[elementNum]] = element
        if lineDict['Process'] != 'L1':
            continue
        else:
            parsedContents.append(lineDict)
    return parsedContents

#Will tell you all the things that are in B,
#if it is not in A
def checkDifferentEDMContents(edmContentsA, edmContentsB):
    return [x for x in edmContentsB if x not in edmContentsA]

def reportToPR(newContents, removedContents, url, theGitHubRequester, isDryRun):
    message = 'Hello, I\'m triggerDoctor. @aloeliger is testing this script for L1T offline software validation.\n\n'
    if newContents == [] and removedContents == []:
        message += 'This PR does not change the EDM content of testing ntuples.'
    else:
        if newContents != []:
            message += 'I found new L1 contents added by this PR:\n'
            message += '| Type | Module | Label | Process |\n'
            message += '|:----:|:------:|:-----:|:-------:|\n'
            for newContent in newContents:
                message+= f'|{newContent["Type"]}|{newContent["Module"]}|{newContent["Label"]}|{newContent["Process"]}\n'
        if removedContents != []:
            message += 'I found removed L1 contents added by this PR:\n'
            message += '| Type | Module | Label | Process |\n'
            message += '|:----:|:------:|:-----:|:-------:|\n'
            for removedContent in removedContents:
                message+= f'|{removedContent["Type"]}|{removedContent["Module"]}|{removedContent["Label"]}|{removedContent["Process"]}\n'
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

    oldNtupleLocation = f'{args.location}/old/src/'
    newNtupleLocation = f'{args.location}/new/src/'

    oldDumpProcess = dumpEventContent(fileLocation=oldNtupleLocation)
    if oldDumpProcess.returncode != 0:
        print('Failed to dump old event content')
        print('stderr:')
        print(oldDumpProcess.stderr.decode())
        print('Return code:')
        print(oldDumpProcess.returncode)
        exit(oldDumpProcess.returncode)
    else:
        oldDumpParse = parseEventContent(oldDumpProcess.stdout.decode())
    
    newDumpProcess = dumpEventContent(fileLocation=newNtupleLocation)
    if newDumpProcess.returncode != 0:
        print('Failed to dump new event content')
        print('stderr:')
        print(newDumpProcess.stderr.decode())
        print('Return code:')
        print(newDumpProcess.returncode)
        exit(newDumpProcess.returncode)
    else:
        newDumpParse = parseEventContent(newDumpProcess.stdout.decode())
    
    newContents = checkDifferentEDMContents(oldDumpParse, newDumpParse)
    removedContents = checkDifferentEDMContents(newDumpParse, oldDumpParse)

    reportToPR(newContents, removedContents, args.prURL, theGitHubRequester, args.dryRun)

    return 0


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description = 'Checks the contents of the two created test ntuples for additional L1 contents')

    parser.add_argument(
        '-l',
        '--location',
        required=True,
        nargs='?',
        help='Location of the test repositories'
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
        help='parse out differences, but do not report to the thread'
    )

    args = parser.parse_args()
    exitCode = main(args)
    exit(exitCode)