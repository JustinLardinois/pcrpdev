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
# appengine_config.py - a component of pCRP

# This script adds the lib/ directory to Python's search path. lib/ is used to
# store third party libraries, which helps to keep the source tree more
# organized.

import site
site.addsitedir("./lib")

from google.appengine.ext import ndb

from pcrp.conference import *
from pcrp.keys import *

conference = Conference(key=metadata_key,name="undefinedCon 2014")
conference.put()