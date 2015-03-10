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
# docs/Makefile - a component of pCRP
# builds PDFs of .tex files in this directory

RM = del

all: manual.pdf

manual.pdf: manual.tex manual.bib
	pdflatex manual.tex
	bibtex manual
	pdflatex manual.tex
	pdflatex manual.tex

spotless: clean
	${RM} *.pdf

clean:
	${RM} *.aux
	${RM} *.bbl
	${RM} *.blg
	${RM} *.log
