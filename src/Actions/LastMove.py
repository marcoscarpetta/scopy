# coding: utf-8

##
# Project: ScoPy - The italian card game 'scopa'
# Author: Marco Scarpetta <marcoscarpetta@mailoo.org>
# Copyright: 2011-2013 Marco Scarpetta
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
from gi.repository import Clutter
from libscopyUI.base import *

Path=_('Edit')
Name=_('Show last move')

def main():
	pass

#nasconde l'ultima presa
def nascondi_ultima_presa(actor, event, app, widget):
	app.partita.hide_last_move()
	widget.set_label(_('Show last move'))
	widget.disconnect_by_func(nascondi_ultima_presa)
	widget.connect('activate', main, app)

#mostra l'ultima presa
def main(widget,app):
	if app.partita.show_last_move() == 0:
		widget.set_label(_('Hide last move'))
		widget.disconnect_by_func(main)
		widget.connect('activate',nascondi_ultima_presa,None,app,widget)
