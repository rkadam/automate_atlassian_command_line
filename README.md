# Automate Atlassian from Command Line (ACL)
Entry to [Atlassian Codegeist Hackathon 2015](http://codegeist.devpost.com/): http://devpost.com/software/atlassian-command-line

# Usage instructions
## How to use this Add On
* Clone source from [Atlassian Command Line](https://github.com/rkadam/atlassian_command_line) git repository
* Install headless browser [PhantomJS](http://phantomjs.org/download.html) if you like to.
* Install [Virtual Environment](http://docs.python-guide.org/en/latest/dev/virtualenvs/)
* create virtual environment for python 2.7+ -> _virtualenv -p /usr/bin/python2.7 venv_
* Install "Atlassian Command Line" as a python module -> _pip install --editable ._
* _Run_ **Atlassian Command Line** from command line as follows:

```
> acl --help
This will provide detail information on all parameters available and how to use ACL
```
![Automate the Atlassian from Command Line -- Help Screen](http://challengepost-s3-challengepost.netdna-ssl.com/photos/production/software_photos/000/309/416/datas/gallery.jpg)

* **Examples**

```
> acl

* In above case, ACL will use all default values as mentioned below:
--base-url=https://pongbot.atlassian.net, --app-type=atlassian.net, --app-name=Confluence, --browser-name=Firefox
```

```
-- Automate Confluence Wiki hosted on *Atlassian.net*
> acl --base-url https://pongbot.atlassian.net --action 'update_general_configuration'
> acl --app-type 'atlassian.net' --base-url https://pongbot.atlassian.net --userid admin --action 'update_global_color_scheme' --action 'update_general_configuration'
```
```
-- Automate on-premise Confluence Wiki ( Update Global Color Scheme )
> acl --app-type other --base-url https://example.com/wiki --userid admin --password admin --action 'update_global_color_scheme'
```
```
-- Automate Global color scheme updates, all wiki spaces color scheme updates, update general configuration (just "title" change right now) of Confluence application
> acl --app-type 'atlassian.net' --base-url https://pongbot.atlassian.net --action 'update_global_color_scheme' --action 'update_wiki_spaces_color_scheme' --action 'update_general_configuration' --userid <userid> --password <password>
```

```
- Automate the act of disabling notification schemes for all JIRA projects
> acl --app-type 'atlassian.net' --base-url https://pongbot.atlassian.net --userid admin --action 'disable_project_notification_schemes' --app-name JIRA --password <password> --browser-name PhantomJS
```

```
- Automate the act of downloading all attachments as per JQL
> acl --app-name JIRA --action get_jira_attachments --userid admin --password pongbot --browser-name PhantomJS --jql "key=TEST-1"
```

```
- Automate JIRA Outgoing Mail Queue check
> acl --app-type 'other' --base-url https://jira.example.com --userid admin --app-name JIRA --password 'password' --browser-name PhantomJS --action 'check_jira_mail_queue_status' --mail_threshold_limit 100
```

```
- Automate JIRA LDAP Sync Status check and Outgoing mail queue check
-   ACL will warn user if LDAP sync status time is greater than default LDAP Threshold limit (4 hours) and Mails in Mail queue are greater than default Mail threshold limit (100 emails)
> acl --app-type 'other' --base-url https://jira.example.com --userid <admin> --app-name JIRA --password 'password' --browser-name PhantomJS --action 'check_jira_mail_queue_status' --action 'check_ldap_sync_status'
```

```
- Automate JIRA LDAP Sync Status check and Outgoing mail queue check against given threshold values
-   ACL will warn user if LDAP sync status time is greater than given LDAP Threshold limit (1 hour) and Mails in Mail queue are greater than given Mail threshold limit (50 emails)
>acl --app-type 'other' --base-url https://jira.example.com --userid <admin> --app-name JIRA --password <password> --browser-name PhantomJS --action 'check_jira_mail_queue_status' --mail-threshold-limit 50 --action 'check_ldap_sync_status' --ldap-sync-threshold-limit 1
```
**Notes**: 
>* Uses _config/wiki_global_custom_colour_scheme.default_ as color scheme file input. Update colors as required.
> * If userid and password are not entered from command line, application will prompt for these values before start of each run.
