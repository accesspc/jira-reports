import re

from lib.tools import Tools

class Confluence():

    def __init__(self, config):
        self.config = config
        self.headers = {
            "Accept": "application/json",
            "Authorization": f"Bearer {self.config.confluence['token']}",
            "Content-Type": "application/json"
        }
        self.users = {}

    def scrapeUserLastLogin(self, username):

        url = f"{self.config.confluence['url']}/admin/users/viewuser.action?username={username}"

        result = Tools().queryGet(url, headers=self.headers)

        if result:
            found = False
            for line in result.text.split("\n"):
                if re.findall(r'Last Updated', line):
                    found = True

                if found:
                    last_login = re.findall(r'class="field-value">(.*)</span>', line)
                    if last_login:
                        return Tools().validateDate(last_login[0])

        else:
            return False
