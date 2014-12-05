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
# pcrp/util.py - a component of pCRP
# utility functions

import datetime
from xml.sax.saxutils import escape

from pcrp.conference_user import *

# function for preventing cross site scripting
html_escape = lambda x: escape(x,
				{'"':"&quot;","'":"&#x27;","/":"&#x2F;","\\":"&92;"})

def is_registered_user(id):
	if(lookup_user(id)): return True
	else: return False

# returns the ConferenceUser object representing the user with
# the supplied id
def lookup_user(id):
	return ConferenceUser.query(ConferenceUser.id == id).get()

# returns datetime object if argument strings compose a valid
# date; returns None otherwise
def parse_datetime(month , day , year , hour , minute):
	try:
		return datetime.datetime(int(month),int(day),int(year),
				int(hour),int(minute))
	except ValueError:
		return None