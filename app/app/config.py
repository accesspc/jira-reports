import json

class Config():

    def __init__(self):
        with open("app/config.json", "r") as cf:
            config = json.load(cf)
            self.audit = config['audit']
            self.confluence = config['confluence']
            self.core = config['core']
            self.jira = config['jira']
            self.queries = config['queries']
