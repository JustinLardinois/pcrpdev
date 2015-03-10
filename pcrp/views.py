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

# variables that will be available in all templates
@app.context_processor
def inject_context():
	google_user = users.get_current_user()
	if google_user:
		current_user = lookup_user(google_user.user_id())
	else:
		current_user = None
	return dict(
		admin        = users.is_current_user_admin(),
		current_user = current_user,
		logout_url   = users.create_logout_url(url_rule["home"]),
		metadata     = keychain["metadata"].get(),
		now          = datetime.datetime.utcnow(),
		url_rule     = url_rule
		)

# TODO: split these up into smaller files
# TODO: find a cleaner way to pass variables to templates
@app.route(url_rule["home"])
def home_view():
	user = users.get_current_user()
	if user: return redirect(url_rule["user_reg"])
	
	return render_template(
		"index.html",
		login_url=users.create_login_url(url_rule["user_reg"])
		)

# handles when the user requests a "clean" form
@app.route(url_rule["user_reg"],methods=["GET"])
@login_required
def user_reg_view_get():
	user = users.get_current_user()
	if is_registered_user(user.user_id()):
		return redirect(url_rule["hub"])

	return render_template(
		"user_reg.html",
		email=user.email()
		)

# handles a processed form; stores data when submission is correct,
# and redirects back to the form with errors when incorrect
@app.route(url_rule["user_reg"],methods=["POST"])
@login_required
def user_reg_view_post():
	google_user = users.get_current_user()
	if is_registered_user(google_user.user_id()):
		return redirect(url_rule["hub"])

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
		pcrp_user.parent = keychain["users"]
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
		return redirect(url_rule["hub"])

	else:
		return render_template(
			"user_reg.html",
			real_name_blank=real_name_blank,
			email_blank=email_blank,
			email_invalid=email_invalid,
			email_in_use=email_in_use,
			affiliation_blank=affiliation_blank,
			real_name=real_name,
			email=email,
			affiliation=affiliation
			)

@app.route(url_rule["admin_panel"])
@login_required
@registration_required
@admin_only
def admin_panel_view():
	return render_template("admin_panel/index.html")

@app.route(url_rule["admin_panel_metadata"],methods=["GET"])
@login_required
@registration_required
@admin_only
def admin_panel_metadata_view_get():
	return render_template(
		"admin_panel/metadata.html",
		update_success=request.args.get("update") == "success",
		deadlines_invalid=request.args.get("deadlines") == "invalid",
		mismatched_deadlines=
			request.args.get("mismatched_deadlines") == "true"
		)

@app.route(url_rule["admin_panel_metadata"],methods=["POST"])
@login_required
@registration_required
@admin_only
def admin_panel_metadata_view_post():
	metadata = keychain["metadata"].get()
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
	
	return redirect(url_rule["admin_panel_metadata"] + arg_string)

@app.route(url_rule["admin_panel_users"],methods=["GET"])
@login_required
@registration_required
@admin_only
def admin_panel_users_view_get():
	metadata=metadata_key.get()
	user = lookup_user(users.get_current_user().user_id())
	conference_users = ConferenceUser.query().fetch()
	return render_template(
		"admin_panel/users.html",
		conference_users=conference_users,
		update_success=request.args.get("update") == "success"
		)

@app.route(url_rule["admin_panel_users"],methods=["POST"])
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
	return redirect(url_rule["admin_panel_users"] + "?update=success")

@app.route(url_rule["hub"])
@login_required
@registration_required
def hub_view():
	program_committee = ConferenceUser.query(
		ConferenceUser.program_committee == True).fetch()

	user = lookup_user(users.get_current_user().user_id())
	your_papers = Paper.query(Paper.author == user.key).fetch()
	
	papers = Paper.query().fetch()
	reviews = [p for p in papers if user.key in p.reviewers]
	
	return render_template(
		"hub.html",
		program_committee=program_committee,
		your_papers=your_papers,
		reviews=reviews
	)

@app.route(url_rule["paper"],methods=["GET"])
@login_required
@registration_required
def paper_view_get():
	metadata = keychain["metadata"].get()
	user = lookup_user(users.get_current_user().user_id())

	paper = None
	filename = None
	reviews = None
	id = request.args.get("id")
	if id == None or id == "":
		return ("No paper ID specified",400)
	elif id == "new":
		if metadata.registration_deadline < datetime.datetime.utcnow():
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
				reviews = [r.get() for r in paper.reviews]
				if paper.file:
					filename = blobstore.BlobInfo.get(paper.file).filename
			else: return ("You do not own this paper",403)
		else: return ("Invalid paper ID",400)

	if paper and metadata.submission_deadline > datetime.datetime.utcnow():
		upload_url = blobstore.create_upload_url(url_rule["paper_upload"]
			+ "?id=" + paper.key.urlsafe())
		# pass key so upload view knows which paper to associate file with
	else:
		upload_url = None

	return render_template(
		"paper.html",
		title=title,
		abstract=abstract,
		id=id,
		additional_authors=additional_authors,
		filename=filename,
		update_success=request.args.get("update") == "success",
		not_pdf=request.args.get("ispdf") == "false",
		reviews=reviews,
		questions=keychain["review_question_list"].get().questions,
		zip=zip
	)

@app.route(url_rule["paper"],methods=["POST"])
@login_required
@registration_required
def paper_view_post():
	metadata = keychain["metadata"].get()
	user = lookup_user(users.get_current_user().user_id())
	
	id = request.form["id"]
	if id == "new":
		if metadata.registration_deadline < datetime.datetime.utcnow():
			return redirect(url_rule["paper"] + "?id=new")
			# delegate errors to GET view
		paper = Paper()
		paper.parent = keychain["papers"]
		paper.author = user.key
		paper.file = None
	else:
		paper = ndb.Key(urlsafe=id).get()
		if not paper or not (paper.author == user.key):
			return redirect(url_rule["paper"] + "?id=" + id)
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
	
	return redirect(url_rule["paper"] + "?id=" + paper.key.urlsafe()
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
	if paper and paper.author == \
		lookup_user(users.get_current_user().user_id()).key:
		if paper.file != None:
			# prevent old versions of file from being orphaned
			blobstore.delete(paper.file)
		paper.file = blob_key
		paper.put()
	
	# paper_view_get() will handle most error scenarios
	return redirect(url_rule["paper"] + "?id=" + paper_key
		+ "&update=success")

@app.route(paper_view_url)
@login_required
@registration_required
def paper_view_view():
	user = lookup_user(users.get_current_user().user_id())
	paper_id = request.args.get("id")
	if not paper_id:
		return ("No paper ID specified",400)
	paper = ndb.Key(urlsafe=paper_id).get()
	if not paper:
		return ("Invalid paper ID",400)
	if paper.author != user.key and not (user.key in paper.reviewers):
		return ("You do not have permission to view this paper",403)
	
	if not paper.file:
		return ("Author did not upload file",404)
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
		real_name=user.real_name,
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
	# list of papers the user does not have a conflict with
	
	prefs = {} # dict of the user's review preferences
	for p in papers:
		key = p.key.urlsafe()
		prefs[key] = p.get_preference(user.id)

	return render_template(
		"review/preferences.html",
		conference_name=metadata.name,
		real_name=user.real_name,
		hub_url=hub_url,
		admin_panel_url=admin_panel_url,
		papers=papers,
		prefs=prefs,
		max_preference=MAX_PREFERENCE + 1,
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
			if pref < 1 or pref > MAX_PREFERENCE: pref = MAX_PREFERENCE // 2
			p.set_preference(user.id,pref)
			p.put()
		except (KeyError,ValueError): pass

	sleep(1)
	# hacky solution to prevent page from rendering before datastore update
	return redirect(preferences_url + "?update=success")

@app.route(assign_url,methods=["GET"])
@login_required
@registration_required
@pc_chair_only
def assign_view_get():
	metadata = metadata_key.get()
	if datetime.datetime.utcnow() < metadata.submission_deadline \
		or metadata.review_deadline < datetime.datetime.utcnow():
		return ("Reviews can only be assigned after the submission deadline "
			"and before the review deadline",403)
	
	user = lookup_user(users.get_current_user().user_id())
	
	return render_template(
		"review/assign.html",
		conference_name=metadata.name,
		real_name=user.real_name,
		hub_url=hub_url,
		admin_panel_url=admin_panel_url,
		papers=Paper.query().fetch(),
		reviewers=ConferenceUser.query(
			ConferenceUser.program_committee == True).fetch(),
		conflicts=conflict_key.get(),
		update_success=request.args.get("update") == "success"
	)

@app.route(assign_url,methods=["POST"])
@login_required
@registration_required
@pc_chair_only
def assign_view_post():
	if request.form["assignment_type"] == "manual":
		papers = Paper.query().fetch()
		for p in papers:
			reviewers = []
			for email in request.form.getlist(p.key.urlsafe()):
				reviewers.append(ConferenceUser.query(
					ConferenceUser.email == email).get().key)
			p.reviewers = reviewers
			p.put()
	elif request.form["assignment_type"] == "auto":
		try:
			reviewer_count = int(request.form["reviewer_count"])
		except ValueError:
			return redirect(assign_url)
		
		conflicts = conflict_key.get()
		papers = Paper.query().fetch()
		for p in papers:
			p.reviewers = [] # clear old assignments to prevent weirdness

		# Greedy algorithm that attempts to assign papers as evenly as
		# possible to reviewers that prefer them the most.
		
		# Does not currently work, not sure why.
		for n in range(reviewer_count):
			for p in papers:
				for m in range(len(papers) + 1): # ranges go from 0 to n-1
					reviewers = reviewer_list(papers,m)
					if len(reviewers) == 0: continue
					likes_best = reduce(
						lambda x,y:
						y if p.get_preference[x] < p.get_preference[y]
						else y,
						reviewers)
					if not conflicts.is_conflict(likes_best,p.author.get().id):
						p.reviewers.append(lookup_user(likes_best).key)
						break
		ndb.put_multi(papers)
	sleep(1) # same hacky bullshit
	return redirect(assign_url + "?update=success")

@app.route(questions_url,methods=["GET"])
@login_required
@registration_required
@pc_chair_only
def questions_view_get():
	metadata = metadata_key.get()
	user = lookup_user(users.get_current_user().user_id())
	questions=review_question_list_key.get()
	
	if datetime.datetime.utcnow() > metadata.submission_deadline:
		return ("Review questions can only be edited before "
			"the paper submission deadline",400)

	return render_template(
		"review/questions.html",
		conference_name=metadata.name,
		real_name=user.real_name,
		hub_url=hub_url,
		admin_panel_url=admin_panel_url,
		questions=review_question_list_key.get().questions,
		update_success=request.args.get("update") == "success"
	)

@app.route(questions_url,methods=["POST"])
@login_required
@registration_required
@pc_chair_only
def questions_view_post():
	questions = []
	for q in request.form.getlist("question"):
		q = q.strip()
		if q != "":
			question = ReviewQuestion()
			question.question = q
			questions.append(question)
	review_questions = review_question_list_key.get()
	review_questions.questions = questions
	review_questions.put()
	return redirect(questions_url + "?update=success")

@app.route(review_url,methods=["GET"])
@login_required
@registration_required
@program_committee_only
def review_view_get():
	metadata = metadata_key.get()
	user = lookup_user(users.get_current_user().user_id())

	if metadata.submission_deadline > datetime.datetime.utcnow():
		return ("Reviews can only be entered after the submission deadline",
			400)
	elif metadata.review_deadline < datetime.datetime.utcnow():
		return ("Review deadline has passed",400)
	id = request.args.get("id")
	if not id or id.strip() == "":
		return ("No paper ID specified",400)
	else:
		id = id.strip()
		paper = ndb.Key(urlsafe=id).get()
		if not paper:
			return ("Invalid paper ID",400)
		else:
			if not (user.key in paper.reviewers):
				return ("You have not been assigned to review this paper",403)
			else:
				filename = None
				if paper.file:
					filename = blobstore.BlobInfo.get(paper.file).filename
				
				answers = None
				for r in paper.reviews:
					if r.get().reviewer == user.key:
						answers = r.get().answers
						break
				return render_template(
					"review/review.html",
					conference_name=metadata.name,
					real_name=user.real_name,
					hub_url=hub_url,
					admin_panel_url=admin_panel_url,
					questions=review_question_list_key.get().questions,
					paper=paper,
					filename=filename,
					paper_view_url=paper_view_url,
					answers=answers,
					zip=zip,
					update_success=request.args.get("update") == "success"
				)

@app.route(review_url,methods=["POST"])
@login_required
@registration_required
@program_committee_only
def review_view_post():
	metadata = metadata_key.get()
	user = lookup_user(users.get_current_user().user_id())
	
	if metadata.submission_deadline > datetime.datetime.utcnow() \
		or metadata.review_deadline < datetime.datetime.utcnow():
		return redirect(review_url)
	id = request.form["id"]
	if not id or id.strip() == "":
		return redirect(review_url)
	id = id.strip()
	paper = ndb.Key(urlsafe=id).get()
	if not paper or not (user.key in paper.reviewers):
		return redirect(review_url + "?id=" + id)
	# delegate error handling to GET view

	review = None
	for r in paper.reviews:
		if r.get().reviewer == user.key:
			review = r.get()
			break
	if not review:
		review = Review()
		review.reviewer = user.key
	review.answers = map(lambda x: x.strip(),request.form.getlist("answer"))
	question_count = len(review_question_list_key.get().questions)
	if len(review.answers) < question_count:
		for n in range(question_count - len(review.answers)):
			review.answers.append("")
	key = review.put()
	if not key in paper.reviews:
		paper.reviews.append(key)
		paper.put()
	return redirect(review_url + "?id=" + id + "&update=success")
