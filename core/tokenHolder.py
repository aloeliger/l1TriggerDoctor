#a quick class to hold the github token for us.

class tokenHolder:
    def __init__(self, tokenLocation='tokens/accessToken.txt'):
        self.tokenLocation = tokenLocation
        with open(tokenLocation) as theFile:
            self.token = theFile.read()
        self.token.rstrip()
        assert(self.token != None and self.token != ''), 'empty token'
    
    def getToken(self):
        return self.token