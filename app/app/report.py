import pandas

from datetime import datetime

from lib.confluence import Confluence
from lib.jira import Jira

class Report():

    def __init__(self, config):
        self.config = config

    def users(self):
        jira = Jira(self.config)

        iteration = 0
        last = False
        users = {}

        while not last:
            # Get result from Users From Group API query
            result = jira.apiGroupMember(iteration)

            # Is it the last iteration
            last = result['isLast']

            # Loop users in result.values
            for u in result['values']:
                # Get and validate last login value
                last_login = jira.scrapeUserLastLogin(u['name'])

                # If a valid date
                if last_login == False:
                    last_login = datetime(2000, 1, 1)

                # If older than config.audit.inactive_days
                if (abs(datetime.today() - last_login)).days >= self.config.audit['inactive_days']:
                    # Create user object
                    user = {
                        "username": u['name'],
                        "displayName": u['displayName'],
                        "emailAddress": u['emailAddress'],
                        "jira_last_login": datetime.strftime(last_login, self.config.audit["date_format"]),
                        "active": u['active'],
                    }
                    # Append user to user dict
                    users[u['name']] = user
                    print(f"jira: add: {user}")

            # Increase iteration number
            iteration += 1

        # Build Confluence users list
        confluence = Confluence(self.config)

        users_list = []
        # Loop Jira users dict
        for k, v in users.items():
            # If confluence audit is enabled
            if self.config.audit['confluence']:
                # Check Confluence last login
                last_login = confluence.scrapeUserLastLogin(v['username'])

                # If older than config.audit.inactive_days
                if last_login and (abs(datetime.today() - last_login)).days >= self.config.audit['inactive_days']:
                    v['confluence_last_login'] = last_login
                    users_list.append(v)
                    print(f"confluence: add: {v}")
                else:
                    print(f"confluence: remove: {v}")

            else:
                users_list.append(v)

        print(f"Audit: Jira Users: {len(users)}")
        if self.config.audit['confluence']:
            print(f"Audit: Jira+Confluence Users: {len(users_list)}")

        # Build CSV from users list
        df = pandas.DataFrame.from_dict(users_list).fillna("n/a")
        columns = list(df.columns.values)

        # Write to CSV artifact
        df.to_csv("users_report.csv", index=False)
