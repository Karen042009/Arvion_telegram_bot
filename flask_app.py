# +++++++++++ FLASK WSGI CONFIGURATION +++++++++++
# This file contains the WSGI configuration required to serve up your
# web app at http://<your-username>.pythonanywhere.com/
# It works by setting the variable 'application' to a WSGI app object.

import sys

# +++ VIRTUALENV +++
# Uncomment the following lines to use your virtualenv.
# replace "venv" with the name of your virtualenv:
#activate_this = '/home/8Khumaryan8/.virtualenvs/my-bot-venv/bin/activate_this.py'
#with open(activate_this) as file_:
#    exec(file_.read(), dict(__file__=activate_this))


# +++ PROJECT HOME +++
# add your project's home directory to the sys.path
#
# Replace '8Khumaryan8' with your PythonAnywhere username
project_home = u'/home/8Khumaryan8/Arvion_Lingua_AI'
if project_home not in sys.path:
    sys.path = [project_home] + sys.path

# +++ FLASK APPLICATION +++
# import the Flask app from your project's file
#
# Replace 'Arvion_Lingua_AI' with the name of your main python file
from Arvion_Lingua_AI.main import app as application