pCRP - Google App Engine-based conference management
====================================================

pCRP is a web app for managing conference paper uploads and reviews. pCRP
is inspired by Eddie Kohler's [HotCRP][1], but is easier to set up and manage
because it runs on Google App Engine, rather than your own Linux server, PHP
runtime, and MySQL server.

All you have to do to set up is run [deps.py](deps.py) and then follow
[Google's instructions for deploying a GAE app][2]. More detailed instructions
can be found in [docs/manual.tex] (docs/manual.tex).

pCRP is licensed under [Version 2.0 of the Apache License](LICENSE).

[1]: http://www.read.seas.harvard.edu/~kohler/hotcrp/
[2]: https://cloud.google.com/appengine/docs/python/tools/uploadinganapp#Python_Uploading_the_app
