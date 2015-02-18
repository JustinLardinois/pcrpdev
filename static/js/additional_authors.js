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

// document is passed as an argument to both functions because
// they would otherwise lack the context for manipulating the DOM

function add_author_field(document)
{
	var field = document.createElement("input");
	field.setAttribute("type","text");
	field.setAttribute("name","additional_authors");
	
	document.getElementById("authors").appendChild(field);
}

function insert_add_button(document)
{
	var button = document.createElement("button");
	button.setAttribute("type","button");
	button.setAttribute("onclick","add_author_field(document)");
		// hacky; relies on the document object being called document,
		// which it should, but you never know
	button.textContent="More Authors";
		// why isn't textContent a function?
	
	var fieldset = document.getElementById("authors");
	fieldset.insertBefore(button,fieldset.childNodes[1]);
		// The aim is to insert the button after the <legend>;
		// I would use insertAfter if such a function existed.
		// It doesn't, so this grabs the second child
		// (which should be the first <input> element
		// and inserts before it.
}
