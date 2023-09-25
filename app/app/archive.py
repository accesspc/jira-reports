from datetime import date
from datetime import timedelta

from lib.jira import Jira
from lib.tools import Tools

class Archive():

    def __init__(self, config):
        self.config = config

    def issues(self, dry_run):

        jira = Jira(self.config)
        tools = Tools()

        # Build the list of issues
        results = {}

        fields = [
            "summary",
            "project",
        ]

        # Build JQL
        exclude_projects = ""
        if len(self.config.jira['archive']['exclude_projects']) > 0:
            exclude_projects = f"project not in ({', '.join(self.config.jira['archive']['exclude_projects'])}) AND "

        statuses = ', '.join(self.config.jira['archive']['statuses'])

        dt = date.today() - timedelta(days=self.config.jira['archive']['days'])

        jql = f"{exclude_projects} status changed TO ({statuses}) DURING ('2000-01-01', '{dt.isoformat()}') AND status in ({statuses})"

        tools.log(f"JQL: {jql}", newLines=True)

        # In case Jira query returns more that maxResults (1000)
        iteration = 0

        while True:

            # Query Jira API
            search = jira.apiSearch(
                jql=jql,
                fields=fields,
                iteration=iteration
            )

            if search:
                result = search.json()

                # Build results dict
                for i in result['issues']:

                    # Add new project
                    if i['fields']['project']['key'] not in results:
                        results[i['fields']['project']['key']] = {
                            'name': i['fields']['project']['name'],
                            'issues': []
                        }

                    # Add issues to project
                    results[i['fields']['project']['key']]['issues'].append({
                        'key': i['key'],
                        'summary': i['fields']['summary']
                    })

                tools.log(f"iteration: {iteration}, maxResult: {result['maxResults']}, total: {result['total']}, issues: {len(result['issues'])}", newLines=True)

                if len(result['issues']) < result['maxResults']:
                    break

                iteration += 1

            else:
                break

        # Sort results for output
        keys = list(results.keys())
        keys.sort()

        # Count archived issues
        c = 0

        # Loop results
        for k in keys:

            # Sort issues
            issues = sorted(results[k]['issues'], key = lambda x: x['key'])

            tools.log(f"project: {k}, issues: {len(issues)}", newLines=True, separator=True)

            # Loop issues
            for i in issues:

                # Archive
                if dry_run:
                    tools.log(f"{self.config.jira['url']}/browse/{i['key']}: '{i['summary']}'")

                else:

                    result = jira.apiIssueArchive(i['key'])

                    if result:
                        c += 1
                        tools.log(f"{result.status_code}: {self.config.jira['url']}/browse/{i['key']}: '{i['summary']}'")
                    else:
                        tools.log(f"failed to archive: {self.config.jira['url']}/browse/{i['key']}", newLines=True)

        tools.log(f"archived: {c}", newLines=True, separator=True)
