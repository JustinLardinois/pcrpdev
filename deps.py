#!/usr/bin/env python
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
# deps.py - a component of pCRP
# uses pip to install pCRP dependencies, as defined in requirements.txt

import pip

REQUIREMENTS_PATH = "requirements.txt"
LIB_PATH          = "lib/"

def install(requirements,lib):
	pip.main(["install","-r",requirements,"-t",lib])

if __name__ == "__main__":
	install(REQUIREMENTS_PATH,LIB_PATH)
