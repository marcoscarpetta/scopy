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
from gi.repository import Gtk
from libscopyUI.base import *

Path=_('File')
Name=_('New game...')
	
def inizia_partita(widget,app,name_entry,var_combo,win_inizio):
		app.opzioni['nome']=name_entry.get_text()
		app.opzioni['variante']=varianti[var_combo.get_active()]
		'''for obj in app.carte.carte:
			obj.object.destroy()
		for box in app.boxes:
			app.boxes[box].clean()
		app.carte = Carte()'''
		app.save()
		win_inizio.destroy()
		app.crea_partita()
		#app.dichiara(app.partita.dai_carte())
		#app.sposta_carte()
		app.partita.start()

def main(widget, app):
	win_inizio = Gtk.Window()
	win_inizio.set_title(_('New game...'))
	win_inizio.set_transient_for(app.window)
	win_inizio.set_position(Gtk.WindowPosition.CENTER_ON_PARENT)
	win_inizio.set_border_width(10)
	win_inizio.connect('delete-event', destroy)
	table=Gtk.Table(2,3,False)
	table.attach(Gtk.Label(_('Name:')),0,1,0,1,Gtk.AttachOptions(0),Gtk.AttachOptions(0))
	table.attach(Gtk.Label(_('Variant:')),0,1,1,2,Gtk.AttachOptions(0),Gtk.AttachOptions(0))
	table.set_row_spacings(5)
	table.set_col_spacings(5)
	name_entry=Gtk.Entry()
	var_combo=Gtk.ComboBoxText()
	for variante in varianti:
		var_combo.append_text(variante)
	table.attach(name_entry,1,2,0,1,Gtk.AttachOptions(4),Gtk.AttachOptions(4))
	table.attach(var_combo,1,2,1,2,Gtk.AttachOptions(4),Gtk.AttachOptions(4))
	button=Gtk.Button()
	button.set_label(_('Start game!'))
	button.connect('pressed',inizia_partita,app,name_entry,var_combo,win_inizio)
	button.connect('activate',inizia_partita,app,name_entry,var_combo,win_inizio)
	table.attach(button,1,2,2,3,Gtk.AttachOptions(0),Gtk.AttachOptions(0))
	win_inizio.add(table)
	name_entry.set_property("activates-default",True)
	button.set_can_default(True)
	button.grab_default()
	#onlineb=Gtk.Button()
	#onlineb.set_label(_('Online game...'))
	#onlineb.connect('pressed',app.show_win_online)
	#table.attach(onlineb,0,1,2,3,Gtk.AttachOptions(0),Gtk.AttachOptions(0))
	var_combo.set_active(varianti.index(app.opzioni['variante']))
	name_entry.set_text(app.opzioni['nome'])
	win_inizio.show_all()
