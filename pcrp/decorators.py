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
# pcrp/decorators.py - a component of pCRP
# decorators used in pcrp/views.py

from functools import wraps

from google.appengine.api import users

from flask import redirect

from pcrp.url_rules import *
from pcrp.util import is_registered_user
from pcrp.util import lookup_user

# To be prepended to view functions. Redirects user to home page
# if not logged in. Thanks to the Flask documentation for help:
# http://flask.pocoo.org/docs/0.10/patterns/viewdecorators/
def login_required(f):
	@wraps(f)
	def decorated_function(*args, **kwargs):
		if not users.get_current_user():
			return redirect(home_url)
		return f(*args, **kwargs)
	return decorated_function

def registration_required(f):
	@wraps(f)
	def decorated_function(*args, **kwargs):
		if not is_registered_user(users.get_current_user().user_id()):
			return redirect(user_reg_url)
		return f(*args, **kwargs)
	return decorated_function

def admin_only(f):
	@wraps(f)
	def decorated_function(*args, **kwargs):
		if not users.is_current_user_admin():
			return ("Administrator privilege is required to access this page",
					403)
		return f(*args, **kwargs)
	return decorated_function

def program_committee_only(f):
	@wraps(f)
	def decorated_function(*args, **kwargs):
		if not (lookup_user(users.get_current_user().user_id())
			.program_committee):
			return ("Only members of the program committee may view this page",
					403)
		return f(*args, **kwargs)
	return decorated_function

def pc_chair_only(f):
	@wraps(f)
	def decorated_function(*args, **kwargs):
		if not (lookup_user(users.get_current_user().user_id()).pc_chair):
			return ("Only program committee chairs may view this page",403)
		return f(*args, **kwargs)
	return decorated_function
