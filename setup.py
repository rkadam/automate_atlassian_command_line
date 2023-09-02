__author__ = 'Raju Kadam'

from setuptools import setup

setup(
    name="Atlassian Command Line",
    version="0.3.2",
    py_modules=['atlassian_command_line'],
    install_requires=['Click', 'requests', 'selenium'],
    entry_points='''
        [console_scripts]
        acl=atlassian_command_line:start
    '''
)