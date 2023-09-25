import statistics

from datetime import date
from datetime import datetime
from datetime import timedelta

from lib.jira import Jira

class ServiceDesk():

    def __init__(self, cache, config):
        self.cache = cache
        self.config = config

    def buildDatesPast12Months(self):

        # Build date ranges filter
        dates = []

        # Current month
        last = date.today()
        first = last.replace(day=1)

        dates.append({
            "first": f"{first.year}/{first.month}/{first.day}",
            "last": f"{last.year}/{last.month}/{last.day}",
            "label": f"{last.year}/{last.month}",
        })

        # First day of this month
        dt = date.today().replace(day=1)

        # Loop past last 12 months
        for i in range(12):

            # Last of previous month
            last = dt - timedelta(days=1)
            # First of previous month
            dt = first = last.replace(day=1)

            dates.append({
                "first": f"{first.year}/{first.month}/{first.day}",
                "last": f"{last.year}/{last.month}/{last.day}",
                "label": f"{last.year}/{last.month}",
            })

        dates.reverse()

        return dates

    def buildDatesYears(self):
        dates = []

        for d in range(self.config.jira['start_year'], date.today().year + 1):
            dates.append({
                "first": f"{d}/01/01",
                "last": f"{d}/12/31",
                "label": f"{d}",
            })

        return dates

    def buildDatesYearlyMonths(self):

        # Dates dict
        dates = {}

        # Today's date for comparison
        dt = date.today()

        # Date for iterate
        di = date(self.config.jira['start_year'], 1, 1)

        # Up until current month
        while di < dt:
            # Get first date
            first = di.replace(day=1)

            # Update di to next month
            di = (di + timedelta(days=35)).replace(day=1)

            # Get last date
            last = di - timedelta(days=1)

            # Add new year list
            if first.year not in dates:
                dates[first.year] = []

            # Add range to dates
            dates[first.year].append({
                "first": f"{first.year}/{first.month}/{first.day}",
                "last": f"{last.year}/{last.month}/{last.day}",
                "label": f"{last.year}/{last.month}",
            })

        return dates

    def buildDatesYearlySprints(self):

        # Dates dict
        dates = {}

        # Today's date for comparison
        dt = date.today()

        # Date for iterate
        di = date(2022, 1, 6)

        # Up until current month
        while di < dt:
            # Get first date
            first = di

            # Get last date
            last = first + timedelta(days=13)

            # Update di
            di = last + timedelta(days=1)

            # Add new year list
            if first.year not in dates:
                dates[first.year] = []
                i = 1

            # Add range to dates
            dates[first.year].append({
                "first": f"{first.year}/{first.month}/{first.day}",
                "last": f"{last.year}/{last.month}/{last.day}",
                "label": f"{first.year}-{first.month}-{first.day}",
            })
            i += 1

        return dates

    def calculateStats(self, values):
        # Size
        stats = {
            'size': len(values)
        }

        # Maximum, Mean
        if len(values) > 0:
            stats['maximum'] = round(max(values), 2)
            stats['mean'] = round(statistics.mean(values), 2)
        else:
            stats['maximum'] = 0
            stats['mean'] = 0

        # Stdev
        if len(values) > 1:
            stats['stdev'] = round(statistics.stdev(values), 2)
        else:
            stats['stdev'] = 0

        # Minimum
        while (0.0 in values):
            values.remove(0.0)

        if len(values) > 0:
            stats['minimum'] = round(min(values), 2)
        else:
            stats['minimum'] = 0

        return stats

    def closedIssuesYearly(self, project, extra, cache):

        # Build projects filter
        project = self.formatProject(project)

        # Build date ranges filter
        dates = self.buildDatesYears()

        return self.queryClosedIssues(project, dates, extra, cache)

    def closedIssuesYearlyMonthly(self, project, extra, cache):

        # Build projects filter
        project = self.formatProject(project)

        # Build date ranges filter
        dates = self.buildDatesYearlyMonths()

        results = {}

        for y, d in dates.items():
            # Query Jira
            results[y] = self.queryClosedIssues(project, d, extra, cache)

        return results

    def formatProject(self, project):

        # Build projects filter
        if type(project) is str:
            return f"'{project}'"

        elif type(project) is list:
            return ",".join(list(map(lambda x: f"'{x}'", project)))

    def queryClosedIssues(self, project, dates, extra, cache=False):

        results = {}

        fields = [
            "summary",
            "status",
        ]

        jira = Jira(self.config)

        for dt in dates:

            first = dt['first']
            last = dt['last']

            # Prepare jql query
            jql = f"project in ({project}) AND status in (Closed, Resolved, Done) AND status changed to (Closed, Resolved, Done) DURING ('{first} 00:00','{last} 23:59') {extra}"

            search = jira.apiSearch(jql, fields)

            if search:
                result = search.json()

                results[dt['label']] = result['total']

                if cache:
                    self.cache.write(
                        run=cache['run'],
                        label=cache['label'],
                        index=dt['label'],
                        value=result['total']
                    )

        print(f"results: {results}")

        return results

    def queryIssueTimingsCustom(self, project, dates, extra, cache):

        # Initiate results dict
        results = {}
        for k in self.config.jira['custom_fields'].keys():
            results[k] = {}

        # Initiate fields list
        fields = [
            "summary",
            "status",
            "created",
        ] + list(map(lambda x: x['field'], self.config.jira['custom_fields'].values()))

        jira = Jira(self.config)

        # Loop dates
        for item in dates.values():
            for dt in item:

                first = dt['first']
                last = dt['last']

                # Prepare jql query
                jql = f"project in ({project}) AND status in (Closed, Resolved, Done) AND status changed to (Closed, Resolved, Done) DURING ('{first} 00:00','{last} 23:59') {extra}"

                search = jira.apiSearch(jql, fields)

                if search:
                    result = search.json()

                    # Init results lists
                    for k in self.config.jira['custom_fields'].keys():
                        results[k][dt['label']] = []

                    for i in result['issues']:
                        # Loop custom fields
                        # Time to: resolution, first response, close after resolution
                        for k in self.config.jira['custom_fields'].keys():
                            field = self.config.jira['custom_fields'][k]['field']
                            if i ['fields'][field] is not None:
                                if len(i['fields'][field]['completedCycles']) > 0:
                                    field_value = 0
                                    for j in i['fields'][field]['completedCycles']:
                                        field_value += j['elapsedTime']['millis']

                                    results[k][dt['label']].append(round(field_value / 1000 / 3600, 2))

        for k, v in results.items():
            for dt in v.keys():
                results[k][dt] = self.calculateStats(results[k][dt])

                self.cache.write(
                    run=cache['run'],
                    label=k,
                    index=dt,
                    value=results[k][dt]
                )

            print(f"results: {k}: {v}")

        return results

    def queryIssueTimingsResolution(self, project, dates, extra, cache):

        # Initiate results dict
        results = {}

        # Initiate fields list
        fields = [
            'summary',
            'status',
            'created',
            'resolutiondate',
        ]

        jira = Jira(self.config)

        # Loop dates
        for item in dates.values():
            for dt in item:

                first = dt['first']
                last = dt['last']

                # Prepare jql query
                jql = f"project in ({project}) AND status in (Closed, Resolved, Done) AND status changed to (Closed, Resolved, Done) DURING ('{first} 00:00','{last} 23:59') {extra}"

                search = jira.apiSearch(jql, fields)

                if search:
                    result = search.json()

                    # Init results list
                    results[dt['label']] = []

                    for i in result['issues']:
                        if i['fields']['resolutiondate'] is not None:
                            ts = datetime.strptime(i['fields']['resolutiondate'], '%Y-%m-%dT%H:%M:%S.000%z') - \
                                datetime.strptime(i['fields']['created'], '%Y-%m-%dT%H:%M:%S.000%z')

                            results[dt['label']].append(round(ts.days + ts.seconds / 86400, 2))

        for k, v in results.items():
            results[k] = self.calculateStats(v)

            self.cache.write(
                run=cache['run'],
                label=cache['label'],
                index=k,
                value=results[k]
            )

        print(f"results: {results}")

        return results

    def runCoreTimingsServiceDesk(self, queries, run):

        # Init data dict
        data = {
            'data': [],
            'labels': [],
        }

        # Build date ranges filter
        dates = self.buildDatesYearlySprints()

        # Loop queries
        for q in queries:

            project = self.formatProject(project=q['project'])

            result = self.queryIssueTimingsCustom(
                project=project,
                dates=dates,
                extra=q['extra'],
                cache={
                    'run': run
                }
            )

            # Loop result by custom_field key
            for k in result.keys():

                # Set labels
                data['labels'] = list(result[k].keys())

                # Append data
                data['data'].append({
                    'data': {
                        'maximum': list(map(lambda x: x['maximum'], result[k].values())),
                        'mean': list(map(lambda x: x['mean'], result[k].values())),
                        'minimum': list(map(lambda x: x['minimum'], result[k].values())),
                        'size': list(map(lambda x: x['size'], result[k].values())),
                        'stdev': list(map(lambda x: x['stdev'], result[k].values())),
                    },
                    'label': self.config.jira['custom_fields'][k]['description'],
                })

        return data

    def runCoreTimingsTeams(self, queries, run):

        # Init data dict
        data = {
            'data': [],
            'labels': []
        }

        # Build date ranges filter
        dates = self.buildDatesYearlySprints()

        # Loop queries
        for q in queries:

            project = self.formatProject(project=q['project'])

            result = self.queryIssueTimingsResolution(
                project=project,
                dates=dates,
                extra=q['extra'],
                cache={
                    'label': q['label'],
                    'run': run
                }
            )

            # Set labels
            data['labels'] = list(result.keys())

            # Append data
            data['data'].append({
                'data': {
                    'maximum': list(map(lambda x: x['maximum'], result.values())),
                    'mean': list(map(lambda x: x['mean'], result.values())),
                    'minimum': list(map(lambda x: x['minimum'], result.values())),
                    'size': list(map(lambda x: x['size'], result.values())),
                    'stdev': list(map(lambda x: x['stdev'], result.values())),
                },
                'label': q['label']
            })

        return data

    def runMonthly(self, queries):

        data = {
            'data': [],
            'labels': [],
        }

        # Build date ranges filter
        dates = self.buildDatesPast12Months()

        for q in queries:

            # Build projects filter
            project = self.formatProject(project=q['project'])

            # Query Jira
            result = self.queryClosedIssues(project, dates, q['extra'])

            # Add results to data.json
            data['labels'] = list(result.keys())
            data['data'].append({
                'data': list(result.values()),
                'label': f"{q['label']} ({sum(result.values())})"
            })

        return data

    def runYearlyComponents(self, queries, run):

        data = {}

        results = {}

        for q in queries:
            result = self.closedIssuesYearly(
                project=self.config.queries['sd']['project'],
                extra=f"{self.config.queries['sd']['extra']} {q['extra']}",
                cache={
                    'label': q['label'],
                    'run': run
                }
            )

            # Build results
            for y, i in result.items():
                # Skip zero entries
                if i != 0:
                    if y in results:
                        results[y][q['label']] = i
                    else:
                        results[y] = {}
                        results[y][q['label']] = i

        # Add results to data.json
        for y, i in results.items():
            # Skip if all results sum to 0
            if sum(i.values()) != 0:
                # Initiate object
                if y not in data:
                    data[y] = {
                        'data': [],
                        'labels': [],
                    }

                # Calculate percentages
                p = {}
                for k, j in i.items():
                    p[k] = j / sum(i.values()) * 100

                data[y]['labels'] = list(map(lambda x: f"{x} ({p[x] :.1f}%)", p.keys()))
                data[y]['data'].append({
                    'data': list(i.values()),
                    'label': y
                })

        return data

    def runYearlyMonthlyComponents(self, queries, run):

        data = {}

        results = {}

        for q in queries:
            result = self.closedIssuesYearlyMonthly(
                project=q['project'],
                extra=q['extra'],
                cache={
                    'label': q['label'],
                    'run': run
                }
            )

            # Build results
            for y, i in result.items():
                if y in results:
                    results[y][q['label']] = i
                else:
                    results[y] = {}
                    results[y][q['label']] = i

        # Add results to data.json
        for y, i in results.items():

            # Check if total year sum > 0
            year_sum = 0

            for a in i.values():
                year_sum += sum(a.values())

            if year_sum == 0:
                continue

            # Initiate object
            if y not in data:
                data[y] = {
                    'data': [],
                    'labels': [],
                }

            # Monthly sums dict
            sums = {}

            for k, j in i.items():
                # Skip if all results sum to 0
                if sum(j.values()) != 0:
                    # Calculate monthly sums
                    for m in j.keys():
                        if m in sums:
                            sums[m] += j[m]
                        else:
                            sums[m] = j[m]

                    data[y]['data'].append({
                        'data': list(j.values()),
                        'label': f"{k} ({sum(j.values())})"
                    })

            # Apply labels
            data[y]['labels'] = list(map(lambda x: f"{datetime.strptime(x, '%Y/%m').strftime('%b')} ({sums[x]})", sums.keys()))

        return data

    def runYearlyStatistics(self, queries, run):

        stats = {}
        for q in queries:
            # Query Jira
            result = self.closedIssuesYearly(
                project=q['project'],
                extra=q['extra'],
                cache={
                    'label': q['label'],
                    'run': run
                }
            )

            # Build stats from result
            for k, v in result.items():
                if k in stats:
                    stats[k][q['label']] = v
                else:
                    stats[k] = {'Year': k}
                    stats[k][q['label']] = v

        return stats
