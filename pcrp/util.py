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

from xml.sax.saxutils import escape

from pcrp.conference_user import *

# function for preventing cross site scripting
html_escape = lambda x: escape(x,
				{'"':"&quot;","'":"&#x27;","/":"&#x2F;","\\":"&92;"})

def is_registered_user(id):
	query = ConferenceUser.query(ConferenceUser.id == id)
	if(query.count() > 0): return True
	else: return False
	