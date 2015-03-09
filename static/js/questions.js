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
// script for adding more question fields on question form

function add_question_field(document)
{
	var field = document.createElement("input");
	field.setAttribute("type","text");
	field.setAttribute("name","question");
	
	document.getElementById("questions").appendChild(field);
}

function insert_add_button(document)
{
	var button = document.createElement("button");
	button.setAttribute("type","button");
	button.setAttribute("onclick","add_question_field(document)");
	button.textContent="More Questions";
	
	var fieldset = document.getElementById("questions");
	fieldset.insertBefore(button,fieldset.childNodes[0])
}
