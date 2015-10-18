# Automate Atlassian from Command Line aka ACL
Entry to [Atlassian Codegeist Hackathon 2015](http://codegeist.devpost.com/): http://devpost.com/software/atlassian-command-line

# Usage instructions
## How to use this Add On
* Clone source from [Atlassian Command Line](https://github.com/rkadam/atlassian_command_line) git repository
* Install headless browser [PhantomJS](http://phantomjs.org/download.html) if you like to.
* Install [Virtual Environment](http://docs.python-guide.org/en/latest/dev/virtualenvs/)
* create virtual environment for python 2.7+
* Install "Atlassian Command Line" as a python module -> pip install --editable .
* _Run_ **Atlassian Command Line** from command line as follows:

```
> acl --help
This will provide detail information on all parameters available and how to use ACL
```
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
- Automate disabling notification schemes for all JIRA projects
> acl --app-type 'atlassian.net' --base-url https://pongbot.atlassian.net --userid admin --action 'disable_project_notification_schemes' --app-name JIRA --password <password> --browser-name PhantomJS
```

**Notes**: 
>* Uses _config/wiki_global_custom_colour_scheme.default_ as color scheme file input. Update colors as required.
> * If userid and password are not entered from command line, application will prompt for these values before start of each run.
