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
from gi.repository import Gtk
from libscopyUI import base

Path=_('File')
Name=_('New game...')

win_inizio = Gtk.Window()
win_inizio.set_title(_('New game...'))
win_inizio.set_border_width(10)
win_inizio.connect('delete-event', base.hide)
table=Gtk.Table(2,4,False)
table.attach(Gtk.Label(_('Name:')),0,1,0,1,Gtk.AttachOptions(0),Gtk.AttachOptions(0))
table.attach(Gtk.Label(_('Variant:')),0,1,1,2,Gtk.AttachOptions(0),Gtk.AttachOptions(0))
table.attach(Gtk.Label(_('Number of players:')),0,1,2,3,Gtk.AttachOptions(0),Gtk.AttachOptions(0))
table.set_row_spacings(5)
table.set_col_spacings(5)
name_entry=Gtk.Entry()
var_combo=Gtk.ComboBoxText()
for variante in base.varianti:
	var_combo.append(variante,variante)
n_players=Gtk.ComboBoxText()
table.attach(name_entry,1,2,0,1,Gtk.AttachOptions(4),Gtk.AttachOptions(4))
table.attach(var_combo,1,2,1,2,Gtk.AttachOptions(4),Gtk.AttachOptions(4))
table.attach(n_players,1,2,2,3,Gtk.AttachOptions(4),Gtk.AttachOptions(4))
button=Gtk.Button()
button.set_label(_('Start game!'))
table.attach(button,1,2,3,4,Gtk.AttachOptions(0),Gtk.AttachOptions(0))
win_inizio.add(table)
name_entry.set_property("activates-default",True)
button.set_can_default(True)
button.grab_default()
	
def set_n_players(widget=None):
	n_players.remove_all()
	for n in base.get_number_of_players(var_combo.get_active_id()):
		n_players.append(str(n),str(n))
	try:
		n_players.set_active_id(base.settings['players'])
	except:
		pass

def inizia_partita(widget,app):
	base.settings['nome']=name_entry.get_text()
	base.settings['variante']=var_combo.get_active_id()
	base.settings['players']=n_players.get_active_id()
	base.settings.save()
	win_inizio.hide()
	app.nuova_partita()

def main(widget, app):
	win_inizio.set_transient_for(app.window)
	win_inizio.set_position(Gtk.WindowPosition.CENTER_ON_PARENT)
	button.connect('pressed',inizia_partita,app)
	button.connect('activate',inizia_partita,app)
	var_combo.connect('changed',set_n_players)
	var_combo.set_active_id(base.settings['variante'])
	name_entry.set_text(base.settings['nome'])
	win_inizio.show_all()
