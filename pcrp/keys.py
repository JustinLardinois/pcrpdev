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
# pcrp/keys.py - a component of pCRP
# contains important global keys

from google.appengine.ext import ndb

from pcrp.models import *

metadata_key             = ndb.Key(Conference,"Metadata")
users_key                = ndb.Key(ConferenceUser,"Users")
conflict_key             = ndb.Key(ConflictSet,"Conflicts")
papers_key               = ndb.Key(Paper,"Papers")
review_question_list_key = ndb.Key(ReviewQuestionList,"Review Questions")

keychain = \
{
	"metadata"             : ndb.Key(Conference,"Metadata"),
	"users"                : ndb.Key(ConferenceUser,"Users"),
	"conflict"             : ndb.Key(ConflictSet,"Conflicts"),
	"papers"               : ndb.Key(Paper,"Papers"),
	"review_question_list" : ndb.Key(ReviewQuestionList,"Review Questions")
}
