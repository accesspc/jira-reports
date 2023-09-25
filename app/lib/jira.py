import re

from lib.tools import Tools

class Jira():

    def __init__(self, config):
        self.config = config
        self.headers = {
            "Accept": "application/json",
            "Authorization": f"Bearer {self.config.jira['token']}",
            "Content-Type": "application/json"
        }

    def apiGroupMember(self, iteration):
        max_results = 50
        start_at = max_results * iteration

        params = {
            "groupname": "jira-software-users",
            "includeInactiveUsers": True,
            "maxResults": max_results,
            "startAt": start_at
        }

        url = f"{self.config.jira['url']}/rest/api/latest/group/member"

        result = Tools().queryGet(url, headers=self.headers, params=params)

        if result:
            return result.json()
        else:
            return False

    def apiIssueArchive(self, issueIdOrKey):

        url = f"{self.config.jira['url']}/rest/api/latest/issue/{issueIdOrKey}/archive"

        result = Tools().queryPut(url, headers=self.headers, status_code=204)

        if result:
            return result
        else:
            return False

    def apiSearch(self, jql, fields, iteration=0):

        max_results = 1000
        start_at = max_results * iteration

        data = {
            "jql": jql,
            "startAt": start_at,
            "maxResults": max_results,
            "fields": fields
        }

        url = f"{self.config.jira['url']}/rest/api/latest/search"

        result = Tools().queryPost(url, headers=self.headers, data=data)

        return result

    def scrapeUserLastLogin(self, username):

        url = f"{self.config.jira['url']}/secure/ViewProfile.jspa?name={username}"

        result = Tools().queryGet(url, headers=self.headers)

        if result:
            last_login = re.findall(r'<dd id="up-d-last-login" class="description">(.*)</dd>', result.text)[0]

            return Tools().validateDate(last_login)
        else:
            return False
