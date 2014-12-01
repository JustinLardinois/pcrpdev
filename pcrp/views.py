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
# pcrp/views.py - a component of pCRP
# In the spirit of following Flask conventions, this script contains all the
# request handlers (known as views) and their routing decorators.

from xml.sax.saxutils import escape

from google.appengine.api import users
from google.appengine.ext import ndb

from flask import redirect
from flask import render_template
from flask import request

from validate_email import validate_email

# Yes, a circular import is necessary:
# http://flask.pocoo.org/docs/0.10/patterns/packages/
from pcrp import app

from pcrp.conference import *
from pcrp.decorators import *
from pcrp.keys import *
from pcrp.url_rules import *

# function for preventing cross site scripting
html_escape = lambda x: escape(x,
				{'"':"&quot;","'":"&#x27;","/":"&#x2F;","\\":"&92;"})

@app.route(home_url)
def home_view():
	metadata = metadata_key.get()
	user = users.get_current_user()
	return render_template(
		"index.html",
		conference_name=metadata.name,
		registration_deadline=metadata.registration_deadline,
		submission_deadline=metadata.submission_deadline,
		user=user,
		create_login_url=lambda x: users.create_login_url(x),
		create_logout_url=lambda x: users.create_logout_url(x)
		)

# handles when the user requests a "clean" form
@app.route(user_reg_url,methods=["GET"])
@login_required
def user_reg_view_get():
	metadata = metadata_key.get()
	return render_template(
		"user_reg.html",
		conference_name=metadata.name,
		email=users.get_current_user().email(),
		html_escape=html_escape
		)

# handles a processed form; stores data when submission is correct,
# and redirects back to the form with errors when incorrect
@app.route(user_reg_url,methods=["POST"])
def user_reg_view_post():
	metadata = metadata_key.get()
	real_name_blank = False
	email_blank = False
	email_invalid = False
	affiliation_blank = False
	
	real_name = request.form["real_name"]
	if(real_name == None): real_name_blank = True
	else:
		real_name = html_escape(real_name).strip()
		if(real_name == ""):
			real_name = None
			real_name_blank = True
	
	email = request.form["email"]
	if(email == None): email_blank = True
	else:
		email = email.strip()
		if(email == ""):
			email = None
			email_blank = True
		elif(not validate_email(email)):
			email_invalid = True
	
	affiliation = request.form["affiliation"]
	if(affiliation == None): affiliation_blank = True
	else:
		affiliation = html_escape(affiliation).strip()
		if(affiliation == ""):
			affiliation = None
			affiliation_blank = True

	if((not real_name_blank) and (not email_blank) 
		and (not email_invalid) and (not affiliation_blank)):
		return "Success!"
	else: return render_template(
			"user_reg.html",
			conference_name=metadata.name,
			real_name_blank=real_name_blank,
			email_blank=email_blank,
			email_invalid=email_invalid,
			affiliation_blank=affiliation_blank,
			real_name=real_name,
			email=email,
			affiliation=affiliation,
			html_escape=html_escape
			)
