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
* Run Atlassian Command Line application
```
acl 'rkadam' 'mypassword' --app-type 'atlassian.net' --baes-url 'https://pongbot.atlassian.net'  
```
