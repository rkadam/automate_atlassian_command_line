# Atlassian Command Line aka ACL
Entry to Atlassian Codegeist Hackathon 2015: http://devpost.com/software/atlassian-command-line

# Usage instructions
* Install headless browser [PhantomJS](http://phantomjs.org/download.html) if you like to.
* Install [Virtual Environment](http://docs.python-guide.org/en/latest/dev/virtualenvs/)
* create virtual environment for python 2.7+
```
virtualenv -p /usr/bin/python2.7 acl_env
source acl_env/bin/activate
```
* Install this application as a module. It will also install all necessary libraries.
```
pip install --editable .
```
* Run Atlassian Command Line application as a module
```
-- Type --help to get details on how to run Atlassian Command Line.
acl --help

-- Just type "acl" to use all default values wherever applicable as mentioned below
-- base-url=https://pongbot.atlassian.net, --app-type=atlassian.net, --app-name=Confluence, --browser-name=Firefox
acl

-- Point to specific Atlassian.net Instance.
acl --base-url https://pongbot.atlassian.net --action 'update_general_configuration'
acl --app-type 'atlassian.net' --base-url https://pongbot.atlassian.net --userid admin --action 'update_global_color_scheme' --action 'update_general_configuration'

-- To automate on-premise Confluence Wiki (Update Global Color Scheme)
acl --app-type other --base-url https://example.com/wiki --userid admin --password admin --action 'update_global_color_scheme'

-- To update color scheme of Confluence application (Global as well as for global wiki spaces)
-- Note: uses config/wiki_global_custom_colour_scheme.default as color scheme input. Update colors as required.
 acl --app-type 'atlassian.net' --base-url https://pongbot.atlassian.net --action 'update_global_color_scheme' --action 'update_wiki_spaces_color_scheme' --userid <userid> --password <password>
 
-- To disable all JIRA project notifications.
acl --app-type other --app-name JIRA --base-url https://example.com/jira --userid admin --password admin --action 'disable_all_project_notifications'

Note: If userid and password are not entered on command line, application will prompt for values before start of each run.
```
* Run as simple python program
```
* Make sure you uncomment section present under "if '__main__' == __name__:"
* Add / Remove functions as necessary perform desired action
```