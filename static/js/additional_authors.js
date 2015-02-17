// Copyright 2014–2015 Justin Lardinois
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//   http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.
///////////////////////////////////////////////////////////////////////////////
// static/js/additional_authors.js
// script for adding more author fields on paper registration form

"use strict";

function add_author_field(d)
{
	var field = d.createElement("input")
	field.setAttribute("type","text")
	field.setAttribute("name","additional_authors")
	
	d.getElementById("additional_authors").appendChild(field)
}

function insert_add_button(d)
{
	var button = d.createElement("button")
	button.setAttribute("type","button")
	button.setAttribute("onclick","add_author_field(" + d + ")")
	button.textContent="More Authors"
	
	var fieldset = d.getElementById("additional_authors")
	fieldset.insertBefore(button,fieldset.childNodes[1])
}
