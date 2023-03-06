# a class to do the actual github api requests
import json
import subprocess
import requests

class gitHubRequestor:
    def __init__(self, theTokenHolder):
        self.theTokenHolder = theTokenHolder
        self.headers = {
            'Accept':'application/vnd.github+json',
            'Authorization': f'Bearer {theTokenHolder.getToken()}',
            'X-GitHub-Api-Version': '2022-11-28',
        }
        self.GITHUB_URL = 'https://api.github.com'


    def getPullRequestInformation(self, url):
        prInfo = url.split('.com/')[1]
        prInfo = prInfo.split('/')
        owner = prInfo[0]
        repo = prInfo[1]
        pr = prInfo[3]
        apiURL = self.GITHUB_URL+f'/repos/{owner}/{repo}/pulls/{pr}'

        resp = requests.get(
            apiURL,
            headers=self.headers
        )
        resultJson = resp.json()
        return resultJson

    def createPullOrIssueComment(self, url, comment):
        info = url.split('.com/')[1]
        info = info.split('/')
        owner = info[0]
        repo = info [1]
        num = info [3]
        apiURL = self.GITHUB_URL+f'/repos/{owner}/{repo}/issues/{num}/comments'

        payload = {"body": comment}

        resp = requests.post(
            apiURL,
            headers=self.headers,
            json=payload
        )
        resultJson = resp.json()
        return resultJson

    #TODO implement other api endpoints