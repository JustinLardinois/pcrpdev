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
# pcrp/util.py - a component of pCRP
# utility functions

import datetime
from xml.sax.saxutils import escape

from pcrp.models import ConferenceUser

# returns number of users who have been assigned to review exactly m each
# from papers
def reviewer_list(papers,x):	
	reviewers = ConferenceUser.query(
		ConferenceUser.program_committee == True).fetch()
	review_count = defaultdict(int)

	for p in papers:
		for r in p.reviewers:
			review_count[r.id] += 1
	return [x for x.id in review_count if review_count[x.id] == M]

def is_registered_user(id):
	if lookup_user(id): return True
	else: return False

# simple sanity check if file is a PDF
# obviously easy to subvert; intended to catch accidental uploads
# of other file types
# assumes that the file's current position is the beginning of the file
def is_pdf(file):
	magic_number = "%PDF"
	return file.read(len(magic_number)) == magic_number

# returns the ConferenceUser object representing the user with
# the supplied id
def lookup_user(id):
	return ConferenceUser.query(ConferenceUser.id == id).get()

# returns datetime object if argument strings compose a valid
# date; returns None otherwise
def parse_datetime(month , day , year , hour , minute):
	try:
		if int(year) < 1900: # datetime.strftime doesn't like pre-1900 years
			return None
		return datetime.datetime(int(year),int(month),int(day),
				int(hour),int(minute))
	except ValueError:
		return None
