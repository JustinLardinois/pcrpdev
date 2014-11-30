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
# pcrp/decorators.py - a component of pCRP
# decorators used in pcrp/views.py

from functools import wraps

from google.appengine.api import users

from flask import redirect

from pcrp.url_rules import *

# To be prepended to view functions. Redirects user to home page
# if not logged in. Thanks to the Flask documentation for help:
# http://flask.pocoo.org/docs/0.10/patterns/viewdecorators/
def login_required(f):
	@wraps(f)
	def decorated_function(*args, **kwargs):
		if (not users.get_current_user()): return redirect(home_url)
		return f(*args, **kwargs)
	return decorated_function