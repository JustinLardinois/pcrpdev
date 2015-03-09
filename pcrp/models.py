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
# pcrp/models.py - a component of pCRP
# classes for NDB models

from google.appengine.ext import ndb

# class that contains conference metadata; initialized
# once in appengine_config.py
class Conference(ndb.Model):
	name = ndb.StringProperty()
	registration_deadline = ndb.DateTimeProperty()
	submission_deadline = ndb.DateTimeProperty()
	review_deadline = ndb.DateTimeProperty()
	home_message = ndb.StringProperty()
	hub_message = ndb.StringProperty()

# Conflicts of interest need only be one-way for there to be an issue.
# For example, while A indicating a conflict with B is different from
# B indicating a conflict with A, either is sufficient for it to be an
# issue.
# This model represents indicated conflicts as a set of pairs of user IDs.
class ConflictSet(ndb.Model):
	conflicts = ndb.PickleProperty()

	def __init__(self):
		ndb.Model.__init__(self)
		self.conflicts = set()

	def add(self,a,b):
		self.conflicts.add(tuple([a,b]))
	
	def delete(self,a,b):
		self.conflicts.discard(tuple([a,b]))
	
	def is_conflict(self,a,b):
		if a == b: return True # users have a conflict with themselves
		x = tuple([a,b])
		y = tuple([b,a])
		return x in self.conflicts or y in self.conflicts

	def is_directed_conflict(self,a,b):
		if a == b: return True
		return tuple([a,b]) in self.conflicts

# class for keeping track of users, since App Engine's native Users class
# is not reliable for long term storage and additional information is needed
class ConferenceUser(ndb.Model):
	nickname = ndb.StringProperty()
	email = ndb.StringProperty()
	real_name = ndb.StringProperty()
	affiliation = ndb.StringProperty()
	id = ndb.StringProperty()
	program_committee = ndb.BooleanProperty()
	pc_chair = ndb.BooleanProperty()

class Paper(ndb.Model):
	title = ndb.StringProperty()
	author = ndb.KeyProperty()
	additional_authors = ndb.StringProperty(repeated=True)
	abstract = ndb.StringProperty()
	file = ndb.BlobKeyProperty()
	preferences = ndb.PickleProperty()
	reviewers = ndb.KeyProperty(repeated=True)
	
	def __init__(self):
		ndb.Model.__init__(self)
		self.preferences = {}
		self.reviewers = []

	def get_preference(self,user_id):
		try: 
			return self.preferences[user_id]
		except KeyError:
			return MAX_PREFERENCE // 2

	def set_preference(self,user_id,preference):
		self.preferences[user_id] = preference

MAX_PREFERENCE = 10
# for paper review preferences; do not change programmatically

class ReviewQuestion(ndb.Model):
	question = ndb.StringProperty()

class ReviewQuestionList(ndb.Model):
	questions = ndb.StructuredProperty(ReviewQuestion,repeated=True)
