import argparse
import subprocess
import os
from core.tokenHolder import tokenHolder
from core.gitHubRequests import gitHubRequester
import json
from core.shellCmsenv import cmsenvCommand

def createCMSSWRelease(release, location, name):
    cmsswCommand = f'scram pro CMSSW {release} -d {location} -n {name}'
    #Create the CMSSW release
    try:
        completedProcess = subprocess.run(
            [cmsswCommand],
            shell=True,
            check=True
        )
    except Exception as err:
        print("Failed to create CMSSW release")
        print(f"\tRelease: {release}")
        print(f"\tLocation: {location}")
        print(f"\tName: {name}")
        print(f'Failed with message: {err}')
        raise
    
    #Now we need to perform the init 
    srcDir = f'{location}/{name}/src/'
    initCommand = f'{cmsenvCommand} && git cms-init'
    
    try:
        initProcess = subprocess.run(
            [initCommand],
            shell=True,
            check=True,
            cwd=srcDir
        )
    except Exception as err:
        print('Failed to properly init CMSSW release')
        print(f"\tRelease: {release}")
        print(f"\tLocation: {location}")
        print(f"\tName: {name}")
        print(f'Failed with message: {err}')
        raise

def performOldReleaseMerge(topPath, baseTag):
    mergeCommand = f'{cmsenvCommand} && git cms-merge-topic -u {baseTag}'
    location = f'{topPath}/old/src/'
    try:
        mergeProcess = subprocess.run(
            [mergeCommand],
            shell=True,
            check=True,
            cwd=location
        )
    except Exception as err:
        print('Failed to properly merge current base tag into the old repository')
        print(f'Top path: {topPath}')
        print(f'Base tag: {baseTag}')
        print(f'Failed with message: {err}')
        raise

def performNewReleaseMerge(topPath, baseTag, headTag):
    mergeCommand = f'{cmsenvCommand} && git cms-merge-topic -u {baseTag}'
    location = f'{topPath}/new/src/'
    try:
        mergeProcess = subprocess.run(
            [mergeCommand],
            shell=True,
            check=True,
            cwd=location
        )
    except Exception as err:
        print('Failed to properly merge current base tag into the new repository')
        print(f'Top path: {topPath}')
        print(f'Base tag: {baseTag}')
        print(f'Failed with message: {err}')
        raise
    
    mergeCommand = f'{cmsenvCommand} && git cms-merge-topic -u {headTag}'
    try:
        mergeProcess = subprocess.run(
            [mergeCommand],
            shell=True,
            check=True,
            cwd=location,
        )
    except Exception as err:
        print('Failed top properly merge head tag into the new repository')
        print(f'Top path: {topPath}')
        print(f'Head tag: {headTag}')
        print(f'Failed with message: {err}')
        raise

def main(args):
    theTokenHolder = tokenHolder()
    theGitHubRequester = gitHubRequester(theTokenHolder)

    #use trigger doctor to get the json information about the PR
    prJSON = theGitHubRequester.getPullRequestInformation(args.prURL)
    newBranch = prJSON["head"]["label"]
    baseBranch = prJSON["base"]["label"]
    prNum = prJSON["number"]
    if args.dryRun:
        print(f'pr: {prNum}')
        print(f'merge: {prJSON["head"]["label"]}')
        print(f'into: {prJSON["base"]["label"]}')
    
    # Create the CMSSW releases necessary
    if not args.dryRun:
        topPath = args.location+f'pr_{prNum}/'
        if not os.path.isdir(topPath):
            os.makedirs(topPath)
        repos = ('old', 'new')
        for name in repos:
            createCMSSWRelease(
                release=args.release,
                location=topPath,
                name=name,
            )
    
    #merge the necessary topics into the necessary repositories
    if not args.dryRun:
        performOldReleaseMerge(
            topPath=topPath,
            baseTag=baseBranch
        )
        
        performNewReleaseMerge(
            topPath = topPath,
            baseTag=baseBranch,
            headTag=newBranch
        )
    print('Complete!')
    return 0


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Creates two CMS releases to test PR commits')

    parser.add_argument(
        '-r',
        '--release',
        required=True,
        nargs='?',
        help='CMSSW release to create tests for'
    )
    parser.add_argument(
        '-p',
        '--prURL',
        required=True,
        nargs='?',
        help='url of the PR to create a test set-up for'
    )
    parser.add_argument(
        '-l',
        '--location',
        required=True,
        nargs='?',
        help='Location to perform the test'
    )
    parser.add_argument(
        '-d',
        '--dryRun',
        action='store_true',
        help='Don\'t perform any of the actual git actions, just print JSON information about the PR to be tested.'
    )

    args = parser.parse_args()

    exitCode = main(args)
    exit(exitCode)