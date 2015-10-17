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
acl --base-url https://pongbot.atlassian.net --action 'update_general_configuration'
acl --base-url https://pongbot.atlassian.net --userid raju.kadam@gmail.com --action 'update_global_color_scheme' --action 'update_general_configuration'
acl --base-url https://localhost:2990 --userid admin --password admin --action 'update_global_color_scheme'
```
* Run as simple python program
```
* Make sure you uncomment section present under "if '__main__' == __name__:"
* Add / Remove functions as necessary perform desired action
```
