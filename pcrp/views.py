# -*- coding: utf-8 -*-
# Copyright 2014–2015 Justin Lardinois
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

from time import sleep

from google.appengine.api import users
from google.appengine.ext import ndb

from flask import redirect
from flask import render_template
from flask import request

from validate_email import validate_email

# Yes, a circular import is necessary:
# http://flask.pocoo.org/docs/0.10/patterns/packages/
from pcrp import app

from pcrp.decorators import *
from pcrp.keys import *
from pcrp.models import *
from pcrp.url_rules import *
from pcrp.util import *

@app.route(home_url)
def home_view():
	metadata = metadata_key.get()
	user = users.get_current_user()
	if user: return redirect(user_reg_url)
	
	return render_template(
		"index.html",
		conference_name=metadata.name,
		registration_deadline=metadata.registration_deadline,
		submission_deadline=metadata.submission_deadline,
		login_url=users.create_login_url(user_reg_url),
		)

# handles when the user requests a "clean" form
@app.route(user_reg_url,methods=["GET"])
@login_required
def user_reg_view_get():
	user = users.get_current_user()
	if is_registered_user(user.user_id()):
		return redirect(hub_url)

	metadata = metadata_key.get()
	return render_template(
		"user_reg.html",
		conference_name=metadata.name,
		email=user.email(),
		html_escape=html_escape,
		logout_url = users.create_logout_url(home_url)
		)

# handles a processed form; stores data when submission is correct,
# and redirects back to the form with errors when incorrect
@app.route(user_reg_url,methods=["POST"])
@login_required
def user_reg_view_post():
	google_user = users.get_current_user()
	if is_registered_user(google_user.user_id()):
		return redirect(hub_url)

	metadata = metadata_key.get()
	real_name_blank = False
	email_blank = False
	email_invalid = False
	affiliation_blank = False
	
	real_name = request.form["real_name"]
	if real_name == None: real_name_blank = True
	else:
		real_name = html_escape(real_name).strip()
		if real_name == "":
			real_name = None
			real_name_blank = True
	
	email = request.form["email"]
	if email == None: email_blank = True
	else:
		email = email.strip()
		if email == "":
			email = None
			email_blank = True
		elif not validate_email(email):
			email_invalid = True
	
	affiliation = request.form["affiliation"]
	if affiliation == None: affiliation_blank = True
	else:
		affiliation = html_escape(affiliation).strip()
		if affiliation == "":
			affiliation = None
			affiliation_blank = True

	if((not real_name_blank) and (not email_blank) 
		and (not email_invalid) and (not affiliation_blank)):
		pcrp_user = ConferenceUser()
		pcrp_user.parent = users_key
		pcrp_user.nickname = google_user.nickname()
		pcrp_user.email = email
		pcrp_user.real_name = real_name
		pcrp_user.affiliation = affiliation
		pcrp_user.id = google_user.user_id()
		pcrp_user.program_committee = False
		pcrp_user.pc_chair = False
		pcrp_user.put()
		sleep(1)
		# Because it takes a while to write to the datastore, there
		# is a bug where the user will be redirected back to the
		# registration page after completing the form. The
		# registration check on hub_view() fails due to the write
		# delay, so the one second sleep should alleviate the bug
		# without annoying users.
		return redirect(hub_url)

	else:
		return render_template(
			"user_reg.html",
			conference_name=metadata.name,
			real_name_blank=real_name_blank,
			email_blank=email_blank,
			email_invalid=email_invalid,
			affiliation_blank=affiliation_blank,
			real_name=real_name,
			email=email,
			affiliation=affiliation,
			html_escape=html_escape,
			logout_url = users.create_logout_url(home_url)
			)

@app.route(admin_panel_url)
@login_required
@registration_required
@admin_only
def admin_panel_view():
	metadata = metadata_key.get()
	user = lookup_user(users.get_current_user().user_id())
	return render_template(
		"admin_panel/index.html",
		conference_name=metadata.name,
		admin_panel_url=admin_panel_url,
		admin_panel_metadata_url=admin_panel_metadata_url,
		admin_panel_users_url=admin_panel_users_url,
		real_name=user.real_name,
		logout_url=users.create_logout_url(home_url)
		)

@app.route(admin_panel_metadata_url,methods=["GET"])
@login_required
@registration_required
@admin_only
def admin_panel_metadata_view_get():
	metadata = metadata_key.get()
	user = lookup_user(users.get_current_user().user_id())
	registration_deadline = metadata.registration_deadline
	submission_deadline = metadata.submission_deadline
	
	return render_template(
		"admin_panel/metadata.html",
		conference_name=metadata.name,
		admin_panel_url=admin_panel_url,
		logout_url=users.create_logout_url(home_url),
		real_name=user.real_name,
		update_success=request.args.get("update") == "success",
		
		registration_deadline_invalid=
			request.args.get("registration_deadline") == "invalid",
		paper_registration_month=registration_deadline.strftime("%m"),
		paper_registration_day=registration_deadline.strftime("%d"),
		paper_registration_year=registration_deadline.strftime("%Y"),
		paper_registration_hour=registration_deadline.strftime("%H"),
		paper_registration_minute=registration_deadline.strftime("%M"),
		
		submission_deadline_invalid=
			request.args.get("submission_deadline") == "invalid",
		paper_submission_month=submission_deadline.strftime("%m"),
		paper_submission_day=submission_deadline.strftime("%d"),
		paper_submission_year=submission_deadline.strftime("%Y"),
		paper_submission_hour=submission_deadline.strftime("%H"),
		paper_submission_minute=submission_deadline.strftime("%M")
		)

@app.route(admin_panel_metadata_url,methods=["POST"])
@login_required
@registration_required
@admin_only
def admin_panel_metadata_view_post():
	metadata = metadata_key.get()
	metadata.name = request.form["conference_name"].strip()
	
	errors = []
	paper_registration_deadline = parse_datetime(
		request.form["paper_registration_month"],
		request.form["paper_registration_day"],
		request.form["paper_registration_year"],
		request.form["paper_registration_hour"],
		request.form["paper_registration_minute"]
	)
	
	if paper_registration_deadline == None:
		errors.append("registration_deadline=invalid")
	else:
		metadata.registration_deadline = paper_registration_deadline

	paper_submission_deadline = parse_datetime(
		request.form["paper_submission_month"],
		request.form["paper_submission_day"],
		request.form["paper_submission_year"],
		request.form["paper_submission_hour"],
		request.form["paper_submission_minute"]
	)
	
	if paper_submission_deadline == None:
		errors.append("submission_deadline=invalid")
	else:
		metadata.submission_deadline = paper_submission_deadline

	metadata.put()
	try:
		arg_string = "?" + reduce((lambda x,y: x + "&" + y),errors)
	except TypeError:
		arg_string = "?update=success"
	
	return redirect(admin_panel_metadata_url + arg_string)

@app.route(admin_panel_users_url,methods=["GET"])
@login_required
@registration_required
@admin_only
def admin_panel_users_view_get():
	metadata=metadata_key.get()
	user = lookup_user(users.get_current_user().user_id())
	conference_users = ConferenceUser.query().fetch()
	return render_template(
		"admin_panel/users.html",
		conference_name=metadata.name,
		admin_panel_url=admin_panel_url,
		logout_url=users.create_logout_url(home_url),
		real_name=user.real_name,
		conference_users=conference_users,
		update_success=request.args.get("update") == "success"
		)

@app.route(admin_panel_users_url,methods=["POST"])
@login_required
@registration_required
@admin_only
def admin_panel_users_view_post():
	conference_users = ConferenceUser.query().fetch()
	for user in conference_users:
		role = request.form["pc_role_" + user.id]
		if role == "no_role":
			user.program_committee = False
			user.pc_chair = False
		elif role == "pc_member":
			user.program_committee = True
			user.pc_chair = False
		elif role == "pc_chair":
			user.program_committee = True
			user.pc_chair = True
		user.put()
	sleep(1) # just in case it needs more time to update
	return redirect(admin_panel_users_url + "?update=success")

@app.route(hub_url)
@login_required
@registration_required
def hub_view():
	return ("<a href=\"" + users.create_logout_url(home_url)
		+ "\">hub hub hub</a>")

@app.route(paper_url)
@login_required
@registration_required
def paper_view():
	metadata=metadata_key.get()
	user = lookup_user(users.get_current_user().user_id())
	return render_template(
		"paper.html",
		conference_name=metadata.name,
		id=""
	)
