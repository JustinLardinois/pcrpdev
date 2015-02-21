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

# class that contains conference metadata; initalized
# once in appengine_config.py

class Conference(ndb.Model):
	name = ndb.StringProperty()
	registration_deadline = ndb.DateTimeProperty()
	submission_deadline = ndb.DateTimeProperty()

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
	author = ndb.StructuredProperty(ConferenceUser)
	additional_authors = ndb.StringProperty(repeated=True)
	abstract = ndb.StringProperty()
	file = ndb.BlobKeyProperty()
