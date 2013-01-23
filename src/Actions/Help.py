# coding: utf-8

##
# Project: ScoPy
# Author: Marco Scarpetta <marcoscarpetta@mailoo.org>
# Copyright: 2012 Marco Scarpetta
# License: GPL-3+
# This program is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the Free
# Software Foundation; either version 3 of the License, or (at your option)
# any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for
# more details.
#
# On Debian GNU/Linux systems, the full text of the GNU General Public License
# can be found in the file /usr/share/common-licenses/GPL-3.
##

from gettext import gettext as _
import os
import webbrowser
from libscopyUI.base import *

Path=_('Help')
Name=_('Help')
	
#caricamento help
lang = os.environ['LANG'][0:2]

def get_path():
	if os.path.exists(percorso_doc+lang+'/index.html'):
		return 'file://'+percorso_doc+lang+'/index.html'
	else:
		return 'file://'+percorso_doc+'it/index.html'

def main(widget,app):
	webbrowser.open(get_path(),2,True)