import argparse
import json
import pandas

from deepmerge import always_merger as Merger

from app.archive import Archive
from app.cache import Cache
from app.config import Config
from app.report import Report
from app.servicedesk import ServiceDesk
from lib.tools import Tools

# Load config from app/config.json file
config = Config()
tools = Tools()

# Get tokens from argument file / variable
parser = argparse.ArgumentParser()
parser.add_argument("filename", type=argparse.FileType('r'))

# Argument sub-parsers
subparsers = parser.add_subparsers(help='service help')

# archive
sp = subparsers.add_parser('archive', help='Archive Jira tickets')
sp.set_defaults(service='archive')
sp.add_argument('-n', '--dry-run', action=argparse.BooleanOptionalAction, default=True)

# service_desk
sp = subparsers.add_parser('service_desk', help='Generate Service Desk report')
sp.set_defaults(service='service_desk')

# user_report
sp = subparsers.add_parser('user_report', help='Generate User report')
sp.set_defaults(service='user_report')
sp.add_argument('-c', '--include-confluence', action=argparse.BooleanOptionalAction, default=False)

args = parser.parse_args()

tokens = json.load(args.filename)

# Merge tokens into config
config.confluence = Merger.merge(config.confluence, tokens['confluence'])
config.jira = Merger.merge(config.jira, tokens['jira'])

# Archive tickets
if "archive" in args.service:

    archive = Archive(config)
    archive.issues(dry_run=args.dry_run)

# Service Desk tickets
elif "service_desk" in args.service:

    cache = Cache()
    data = {}
    servicedesk = ServiceDesk(cache, config)

    #
    # Yearly: Statistics
    #
    tools.log("data: yearly_statistics, def: runYearlyStatistics: closedIssuesYearly: queryClosedIssues", newLines=True, separator=True)

    # SD + Issue Types for all Core Projects
    queries = []
    queries.append(config.queries['sd'])
    for t in config.queries['types']:
        t['project'] = config.core['projects']
        queries.append(t)

    stats = servicedesk.runYearlyStatistics(
        queries=queries,
        run='yearly_statistics'
    )

    # Convert stats to html table
    df = pandas.DataFrame.from_dict(list(stats.values())).fillna(0)
    data['yearly_statistics'] = df.to_html(classes="table table-striped table-hover", index=False, justify="left")

    #
    # Monthly: Closed
    #
    tools.log("data: monthly_closed, def: runMonthly: queryClosedIssues", newLines=True, separator=True)

    # SD + Teams
    queries = [config.queries['sd']] + config.queries['teams']

    data['monthly_closed'] = servicedesk.runMonthly(
        queries=queries
    )

    #
    # Monthly: continued service by issue type: Bug, Technical Dept, Upgrade/Patch
    #
    tools.log("data: monthly_continued_service, def: runMonthly: queryClosedIssues", newLines=True, separator=True)

    # Issue Types for all Core Projects
    queries = []
    for t in config.queries['types']:
        t['project'] = config.core['projects']
        queries.append(t)

    data['monthly_continued_service'] = servicedesk.runMonthly(
        queries=queries
    )

    #
    # Core: timings: sd
    #
    tools.log("data: sprint_core_timings_sd, def: runCoreTimingsServiceDesk: queryIssueTimingsCustom", newLines=True, separator=True)

    data['sprint_core_timings_sd'] = servicedesk.runCoreTimingsServiceDesk(
        queries=[config.queries['sd']],
        run='sprint_core_timings_sd'
    )

    #
    # Core: timings: teams
    #
    tools.log("data: sprint_core_timings_teams, def: runCoreTimingsTeams: queryIssueTimingsResolution", newLines=True, separator=True)

    data['sprint_core_timings_teams'] = servicedesk.runCoreTimingsTeams(
        queries=config.queries['teams'],
        run='sprint_core_timings_teams'
    )

    #
    #
    # Yearly: Support Live vs Non-Live
    #
    tools.log("data: yearly_support_live, def: runYearlyComponents: closedIssuesYearly: queryClosedIssues", newLines=True, separator=True)

    data['yearly_support_live'] = servicedesk.runYearlyComponents(
        queries=config.queries['live'],
        run='yearly_support_live'
    )

    #
    # Yearly.Monthly: Support by component
    #
    tools.log("data: monthly_support_components, def: runYearlyMonthlyComponents: closedIssuesYearlyMonthly: queryClosedIssues", newLines=True, separator=True)

    queries = []
    for c in config.queries['components']:
        q = c.copy()
        q['project'] = config.queries['sd']['project']
        q['extra'] = f"{config.queries['sd']['extra']} {c['extra']}"
        queries.append(q)

    data['monthly_support_components'] = servicedesk.runYearlyMonthlyComponents(
        queries=queries,
        run='monthly_support_components'
    )

    #
    # Yearly.Monthly: Teams by component
    #
    tools.log("data: monthly_teams_components, def: runYearlyMonthlyComponents: closedIssuesYearlyMonthly: queryClosedIssues", newLines=True, separator=True)

    queries = []
    for c in config.queries['components']:
        q = c.copy()
        if 'project' not in q:
            q['project'] = config.core['projects']
        queries.append(q)

    data['monthly_teams_components'] = servicedesk.runYearlyMonthlyComponents(
        queries=queries,
        run='monthly_teams_components'
    )

    #
    # Write stats to json file
    #
    with open('docs/data/jira.json', 'w') as f:
        f.write(json.dumps(data))

    cache.save()

# User Report
elif "user_report" in args.service:
    if args.include_confluence:
        config.audit['confluence'] = True

    report = Report(config)
    report.users()

else:
    tools.log("No service selected", newLines=True)
