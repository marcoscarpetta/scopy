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
from gi.repository import Clutter
from libscopyUI.base import *

Path=_('Edit')
Name=_('Show last move')

def main():
	pass

#nasconde l'ultima presa
def nascondi_ultima_presa(actor, event, app, widget, oggetti, index):
	app.delete(index)
	widget.set_label(_('Show last move'))
	widget.disconnect_by_func(nascondi_ultima_presa)
	widget.connect('activate', main, app)
	for obj in oggetti:
		obj.destroy()
	i=app.stage.get_n_children()
	n=0
	while n<i:
		app.stage.get_nth_child(n).show()
		n=n+1

#mostra l'ultima presa
def main(widget,app):
	if app.ultima_presa[0] != 0:
		widget.set_label(_('Hide last move'))
		i=app.stage.get_n_children()
		n=0
		while n<i:
			if app.stage.get_nth_child(n) != app.back_img:
				app.stage.get_nth_child(n).hide()
			n=n+1
		index = app.comunica(_('Computer played ... and took ...'),0)
		oggetti=[]
		actor = Clutter.Texture.new_from_file(percorso_carte+app.opzioni['carte']+'/'+immagini[app.ultima_presa[0][0]][app.ultima_presa[0][1]])
		actor.set_position(10,10)
		actor.set_reactive(True)
		app.stage.add_actor(actor)
		actor.connect('button-press-event',nascondi_ultima_presa,app,widget,oggetti)
		oggetti.append(actor)
		i=0
		while i < len(app.ultima_presa[1]):
			actor = Clutter.Texture.new_from_file(percorso_carte+app.opzioni['carte']+'/'+immagini[app.ultima_presa[1][i][0]][app.ultima_presa[1][i][1]])
			actor.set_position(10+i*70,160)
			actor.set_reactive(True)
			app.stage.add_actor(actor)
			actor.connect('button-press-event',nascondi_ultima_presa,app,widget,oggetti,index)
			oggetti.append(actor)
			i=i+1
		widget.disconnect_by_func(main)
		widget.connect('activate', nascondi_ultima_presa,None,app,widget,oggetti,index)