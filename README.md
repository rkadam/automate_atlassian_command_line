# Atlassian Command Line aka ACL
Entry to Atlassian Codegeist Hackathon 2015: http://devpost.com/software/atlassian-command-line

# Usage instructions
* Install [Virtual Environment](http://docs.python-guide.org/en/latest/dev/virtualenvs/)
* create virtual environment for python 2.7+
`
virtualenv -p /usr/bin/python2.7 acl_env
source acl_env/bin/activate
`
* Install necessary python libraries.
`
pip install requests
pip install selenium 
`
* Install headless browser (PhantomJS)[http://phantomjs.org/download.html] if you like to.
* Run Atlassian Command Line application
`
