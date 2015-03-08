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

import datetime
from time import sleep

from google.appengine.api import users
from google.appengine.ext import blobstore
from google.appengine.ext import ndb

from flask import make_response
from flask import redirect
from flask import render_template
from flask import request

from werkzeug import parse_options_header

from validate_email import validate_email

# Yes, a circular import is necessary:
# http://flask.pocoo.org/docs/0.10/patterns/packages/
from pcrp import app

from pcrp.decorators import *
from pcrp.keys import *
from pcrp.models import *
from pcrp.url_rules import *
from pcrp.util import *

# TODO: split these up into smaller files
# TODO: find a cleaner way to pass variables to templates
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
		review_deadline=metadata.review_deadline,
		login_url=users.create_login_url(user_reg_url),
		home_message=metadata.home_message
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
	email_in_use = False
	
	real_name = request.form["real_name"]
	if real_name == None: real_name_blank = True
	else:
		real_name = real_name.strip()
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
		elif ConferenceUser.query(ConferenceUser.email == email).get():
			email_in_use = True
	
	affiliation = request.form["affiliation"]
	if affiliation == None: affiliation_blank = True
	else:
		affiliation = affiliation.strip()
		if affiliation == "":
			affiliation = None
			affiliation_blank = True

	if((not real_name_blank) and (not email_blank) 
		and (not email_invalid) and (not affiliation_blank)
		and (not email_in_use)):
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
			email_in_use=email_in_use,
			affiliation_blank=affiliation_blank,
			real_name=real_name,
			email=email,
			affiliation=affiliation,
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
		hub_url=hub_url,
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
	review_deadline = metadata.review_deadline
	
	return render_template(
		"admin_panel/metadata.html",
		conference_name=metadata.name,
		admin_panel_url=admin_panel_url,
		hub_url=hub_url,
		logout_url=users.create_logout_url(home_url),
		real_name=user.real_name,
		update_success=request.args.get("update") == "success",
		deadlines_invalid=request.args.get("deadlines") == "invalid",
		mismatched_deadlines=
			request.args.get("mismatched_deadlines") == "true",

		paper_registration_month=registration_deadline.strftime("%m"),
		paper_registration_day=registration_deadline.strftime("%d"),
		paper_registration_year=registration_deadline.strftime("%Y"),
		paper_registration_hour=registration_deadline.strftime("%H"),
		paper_registration_minute=registration_deadline.strftime("%M"),
		
		paper_submission_month=submission_deadline.strftime("%m"),
		paper_submission_day=submission_deadline.strftime("%d"),
		paper_submission_year=submission_deadline.strftime("%Y"),
		paper_submission_hour=submission_deadline.strftime("%H"),
		paper_submission_minute=submission_deadline.strftime("%M"),
		
		paper_review_month=review_deadline.strftime("%m"),
		paper_review_day=review_deadline.strftime("%d"),
		paper_review_year=review_deadline.strftime("%Y"),
		paper_review_hour=review_deadline.strftime("%H"),
		paper_review_minute=review_deadline.strftime("%M"),
		
		home_message=metadata.home_message,
		hub_message=metadata.hub_message
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

	paper_submission_deadline = parse_datetime(
		request.form["paper_submission_month"],
		request.form["paper_submission_day"],
		request.form["paper_submission_year"],
		request.form["paper_submission_hour"],
		request.form["paper_submission_minute"]
	)
	
	paper_review_deadline = parse_datetime(
		request.form["paper_review_month"],
		request.form["paper_review_day"],
		request.form["paper_review_year"],
		request.form["paper_review_hour"],
		request.form["paper_review_minute"]
	)
	
	if not (paper_registration_deadline and paper_submission_deadline 
		and paper_review_deadline):
		errors.append("deadlines=invalid")
	else:
		if paper_registration_deadline < paper_submission_deadline \
			and paper_submission_deadline < paper_review_deadline:
			metadata.registration_deadline = paper_registration_deadline
			metadata.submission_deadline = paper_submission_deadline
			metadata.review_deadline = paper_review_deadline
		else:
			errors.append("mismatched_deadlines=true")

	if request.form["home_message"]:
		metadata.home_message = request.form["home_message"].strip()
	else:
		metadata.home_message = ""
	
	if request.form["hub_message"]:
		metadata.hub_message = request.form["hub_message"].strip()
	else:
		metadata.hub_message = ""

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
		hub_url=hub_url,
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
	metadata = metadata_key.get()
	user = lookup_user(users.get_current_user().user_id())
	program_committee = ConferenceUser.query(
		ConferenceUser.program_committee == True).fetch()
	before_registration_deadline = \
		metadata.registration_deadline > datetime.datetime.utcnow()
	your_papers = Paper.query(Paper.author == user.key).fetch()
	
	return render_template(
		"hub.html",
		conference_name=metadata.name,
		registration_deadline=metadata.registration_deadline,
		submission_deadline=metadata.submission_deadline,
		review_deadline=metadata.review_deadline,
		real_name=user.real_name,
		admin=users.is_current_user_admin(),
		logout_url=users.create_logout_url(home_url),
		admin_panel_url=admin_panel_url,
		program_committee=program_committee,
		before_registration_deadline=before_registration_deadline,
		paper_url=paper_url,
		your_papers=your_papers,
		conflicts_url=conflicts_url,
		hub_message=metadata.hub_message
	)

@app.route(paper_url,methods=["GET"])
@login_required
@registration_required
def paper_view_get():
	metadata=metadata_key.get()
	registration_deadline = metadata.registration_deadline
	submission_deadline = metadata.submission_deadline
	review_deadline = metadata.review_deadline
	user = lookup_user(users.get_current_user().user_id())

	paper = None
	filename = None
	id = request.args.get("id")
	if id == None or id == "":
		return ("No paper ID specified",400)
	elif id == "new":
		if registration_deadline < datetime.datetime.utcnow():
			return ("Registration deadline has passed",400)
		title = ""
		abstract = ""
		additional_authors = []
	else:
		paper = ndb.Key(urlsafe=id).get()
		if paper:
			if paper.author.get().id == user.id:
				title = paper.title
				abstract = paper.abstract
				additional_authors = paper.additional_authors
				if paper.file:
					filename = blobstore.BlobInfo.get(paper.file).filename
			else: return ("You do not own this paper",403)
		else: return ("Invalid paper ID",400)

	if paper and submission_deadline > datetime.datetime.utcnow():
		upload_url = blobstore.create_upload_url(paper_upload_url
			+ "?id=" + paper.key.urlsafe())
		# pass key so upload view knows which paper to associate file with
	else:
		upload_url = None

	return render_template(
		"paper.html",
		conference_name=metadata.name,
		admin_panel_url=admin_panel_url,
		logout_url=users.create_logout_url(home_url),
		hub_url=hub_url,
		paper_view_url=paper_view_url,
		real_name=user.real_name,
		title=title,
		abstract=abstract,
		id=id,
		additional_authors=additional_authors,
		filename=filename,
		registration_deadline=registration_deadline,
		submission_deadline=submission_deadline,
		review_deadline=review_deadline,
		before_registration_deadline=(registration_deadline >
			datetime.datetime.utcnow()),
		before_submission_deadline=(submission_deadline >
			datetime.datetime.utcnow()),
		admin=users.is_current_user_admin(),
		upload_url=upload_url,
		update_success=request.args.get("update") == "success",
		not_pdf=request.args.get("ispdf") == "false"
	)

@app.route(paper_url,methods=["POST"])
@login_required
@registration_required
def paper_view_post():
	metadata=metadata_key.get()
	registration_deadline = metadata.registration_deadline
	submission_deadline = metadata.submission_deadline
	user = lookup_user(users.get_current_user().user_id())
	
	id = request.form["id"]
	if id == "new":
		if registration_deadline < datetime.datetime.utcnow():
			return redirect(paper_url + "?id=new")
			# delegate errors to GET view
		paper = Paper()
		paper.parent = papers_key
		paper.author = user.key
		paper.file = None
	else:
		paper = ndb.Key(urlsafe=id).get()
		if not paper or not paper.author.id == user.id:
			return redirect(paper_url + "?id=" + id)
			# delegate errors to GET view

	title = request.form["title"]
	if title != None and title.strip() != "":
		paper.title = request.form["title"].strip()
	else: paper.title = "Untitled Paper"

	additional_authors = []
	for a in request.form.getlist("additional_authors"):
		if a != None and a.strip() != "":
			additional_authors.append(a.strip())
	paper.additional_authors = additional_authors

	abstract = request.form["abstract"]
	if abstract != None and abstract.strip() != "":
		paper.abstract = abstract.strip()
	else: paper.abstract = ""
	
	paper.put()
	
	return redirect(paper_url + "?id=" + paper.key.urlsafe()
		+ "&update=success")

@app.route(paper_upload_url,methods=["POST"])
@login_required
@registration_required
def paper_upload_view():
	# big thanks to Stack Overflow user Koffee for explaining how this works
	# http://stackoverflow.com/a/18073466/2752467
	f = request.files['file']
	header = f.headers['Content-Type']
	parsed_header = parse_options_header(header)
	blob_key = blobstore.BlobKey(parsed_header[1]['blob-key'])
	
	paper_key = request.args.get("id")
	paper = ndb.Key(urlsafe=paper_key).get()

	blob_stream = blobstore.BlobReader(blob_key)
	if not is_pdf(blob_stream):
		blob_stream.close()
		blobstore.delete(blob_key)
		return redirect(paper_url + "?id=" + paper_key + "&ispdf=false")
	blob_stream.close()

	# sanity check: file is associated with a paper owned by the current user
	if paper and paper.author.id == users.get_current_user().user_id():
		if paper.file != None:
			# prevent old versions of file from being orphaned
			blobstore.delete(paper.file)
		paper.file = blob_key
		paper.put()
	
	# paper_view_get() will handle most error scenarios
	return redirect(paper_url + "?id=" + paper_key + "&update=success")

@app.route(paper_view_url)
@login_required
@registration_required
def paper_view_view():
	paper_id = request.args.get("id")
	if not paper_id:
		return redirect(paper_url)
	paper = ndb.Key(urlsafe=paper_id).get()
	if not paper or paper.author.id != users.get_current_user().user_id():
		return redirect(paper_url + "?id=" + paper_id)
		# delegate errors to paper_view_get()
	
	blob_info = blobstore.BlobInfo.get(paper.file)
	response = make_response(blob_info.open().read())
	
	# force MIME type to PDF, so that even if a user somehow manages to
	# upload a non-PDF, viewers will get garbage rather than a
	# correctly-rendered non-PDF
	response.headers['Content-Type'] = "application/pdf"
	return response

@app.route(conflicts_url,methods=["GET"])
@login_required
@registration_required
def conflicts_view_get():
	metadata = metadata_key.get()
	user = lookup_user(users.get_current_user().user_id())
	other_users = ConferenceUser.query(ConferenceUser.id != user.id).fetch()
	conflicts = conflict_key.get()

	return render_template(
		"conflicts.html",
		conference_name=metadata.name,
		users=other_users,
		conflicts=conflicts,
		user_id=user.id,
		hub_url=hub_url,
		admin_panel_url=admin_panel_url,
		logout_url=users.create_logout_url(home_url),
		real_name=user.real_name,
		admin=users.is_current_user_admin(),
		update_success=request.args.get("update") == "success"
	)

@app.route(conflicts_url,methods=["POST"])
@login_required
@registration_required
def conflicts_view_post():
	user_id = users.get_current_user().user_id()
	stored_conflicts = conflict_key.get()

	submitted_conflicts = set()
	# all conflicts that were indicated in submitted form
	for email in request.form.getlist("conflicts"):
		submitted_id = ConferenceUser.query(
			ConferenceUser.email == email).get().id
		submitted_conflicts.add(submitted_id)
		stored_conflicts.add(user_id,submitted_id)

	all_users = set()
	# all users that are not the current user
	for user in ConferenceUser.query(ConferenceUser.id != user_id).fetch():
		all_users.add(user.id)

	unconflicted = all_users - submitted_conflicts
	# users who were not marked in the form
	for user in unconflicted:
		stored_conflicts.delete(user_id,user)
	
	stored_conflicts.put()
	return redirect(conflicts_url + "?update=success")

@app.route(preferences_url,methods=["GET"])
@login_required
@registration_required
@program_committee_only
def preferences_view_get():
	metadata = metadata_key.get()
	if datetime.datetime.utcnow() < metadata.registration_deadline \
		or datetime.datetime.utcnow() > metadata.submission_deadline:
		return ("Review preferences can only be entered after the "
			"paper registration deadline and before the paper submission "
			"deadline",403)
	
	user = lookup_user(users.get_current_user().user_id())
	conflicts = conflict_key.get()
	
	papers = Paper.query(Paper.author != user.key).fetch()
	papers = [p for p in papers if not conflicts.is_conflict(user.id,
		p.author.get().id)]
	prefs = {}
	for p in papers:
		key = p.key.urlsafe()
		try:
			pref = p.get_preference(user.id)
			prefs[key] = pref
		except KeyError:
			prefs[key] = 5

	return render_template(
		"review/preferences.html",
		conference_name=metadata.name,
		real_name=user.real_name,
		hub_url=hub_url,
		admin=users.is_current_user_admin(),
		admin_panel_url=admin_panel_url,
		logout_url=users.create_logout_url(home_url),
		papers=papers,
		prefs=prefs,
		update_success=request.args.get("update") == "success"
	)

@app.route(preferences_url,methods=["POST"])
@login_required
@registration_required
@program_committee_only
def preferences_view_post():
	user = lookup_user(users.get_current_user().user_id())
	conflicts = conflict_key.get()
	papers = Paper.query(Paper.author != user.key).fetch()
	papers = [p for p in papers if not conflicts.is_conflict(user.id,
		p.author.get().id)]
	
	for p in papers:
		try:
			pref = int(request.form[p.key.urlsafe()])
			p.set_preference(user.id,pref)
			p.put()
		except (KeyError,ValueError): pass

	return redirect(preferences_url + "?update=success")
