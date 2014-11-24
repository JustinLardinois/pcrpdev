# Copyright 2014 Justin Lardinois
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
###############################################################################
# pcrp/__init__.py - a component of pCRP

from google.appengine.api import users
from google.appengine.ext import ndb

from flask import Flask
from flask import render_template

from pcrp.conference import *
from pcrp.keys import *

app = Flask("pcrp")

@app.route("/")
def hello():
	metadata = metadata_key.get()
	user = users.get_current_user()
	return render_template("index.html",
		conference_name=metadata.name,
		registration_deadline=metadata.registration_deadline,
		submission_deadline=metadata.submission_deadline,
		user=user,
		create_login_url=lambda x: users.create_login_url(x),
		create_logout_url=lambda x: users.create_logout_url(x))
