# Jira reports

Jira reports is run on a schedule every weekday at 08:45. This include the following jobs:

* archive
* service_desk
* user_report

## Jira issue archival

Issues are archived based on the criteria defined in the [config.json](./app/config.json) under `.jira.archive`. Current settings are:

* Archive issues older than 365 days
* Exclude projects:
    * Personal
    * Private
* Archive issues that are in statuses:
    * Closed
    * Done
    * Resolved
