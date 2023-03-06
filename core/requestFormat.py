#a quick class for getting a formatted request for github

class requestFormatter:
    def __init__(self, token):
        self.coreRequest = [
        'curl',
        '-L',
        '-H "Accept: application/vnd.github+json"',
        f'-H "Authorization: Bearer {token}"',
        '-H "X-GitHub-Api-Version: 2022-11-28"',
        ]
    def getCoreRequest(self):
        return self.coreRequest.copy()

    #TODO verify all formatted requests are correct.
    def getPOSTRequest(self):
        command = self.getCoreRequest()
        command.append('-X POST')
        return command.copy()
    
    def getGETRequest(self):
        command = self.getCoreRequest()
        command.append('-X GET')
        return command.copy()
    
    def getPUTRequest(self):
        command = self.getCoreRequest()
        command.append('-X PUT')
        return command.copy()

    def getPATCHRequest(self):
        command = self.getCoreRequest()
        command.append('-X PATCH')
        return command.copy()

    def getDELETERequest(self):
        command = self.getCoreRequest()
        command.append('-X DELETE')
        return command.copy()