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
# appengine_config.py - a component of pCRP
# App Engine initialization code; due to the nature of App Engine, this is the
# only place to put code that should only be run once when the app is first
# deployed.

# adds the lib/ directory to Python's search path. lib/ is used to store third
# party libraries, which helps to keep the source tree more organized.
import site
site.addsitedir("./lib")

import datetime

from google.appengine.ext import ndb

from pcrp.keys import conflict_key
from pcrp.keys import metadata_key
from pcrp.models import Conference
from pcrp.models import ConflictSet

# default time value; should be changed in administrator panel
end_of_time = datetime.datetime(datetime.MAXYEAR,12,12,23,59,59,0)

# initializes conference metadata so the app initially has something
# to work with
conference = metadata_key.get()
if not conference:
	conference = Conference()
	conference.key = metadata_key
	conference.name = "undefinedCon 2014"
	conference.registration_deadline = end_of_time
	conference.submission_deadline = end_of_time
	conference.registration_deadline = end_of_time
	conference.home_message = ""
	conference.hub_messagge = ""
	conference.put()

conflicts = conflict_key.get()
if not conflicts:
	conflicts = ConflictSet()
	conflicts.key = conflict_key
	conflicts.put()

review_questions = review_question_list_key.get()
if not review_questions:
	review_questions = ReviewQuestionList()
	review_questions.questions = []
	review_questions.put()
