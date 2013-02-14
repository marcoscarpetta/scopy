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
from libscopyUI.base import *

Path=_('Edit')
Name=_('Settings')
	
#modifica le preferenze in base ai valori dati dall'utente
def modifica_preferenze(widget,app,carte_combo,velocita,sfondi_combo,win_pre):
	if settings['cards'] != tipi_di_carte[carte_combo.get_active()]:
		settings['cards'] = tipi_di_carte[carte_combo.get_active()]
		if app.partita != None:
			app.partita.update_cards()
	settings['speed']=str(velocita.get_value())
	settings['sfondo']=sfondi[sfondi_combo.get_active()]
	app.back_img.set_from_file(percorso_tap+settings['sfondo']+'.png')
	settings.save()
	win_pre.destroy()

def main(widget, app):
	win_pre = Gtk.Window()
	win_pre.set_title(_('Edit Settings'))
	win_pre.set_transient_for(app.window)
	win_pre.set_position(Gtk.WindowPosition.CENTER_ON_PARENT)
	win_pre.set_border_width(10)
	win_pre.connect('delete-event', destroy)
	table=Gtk.Table(2,5,False)
	table.set_row_spacings(5)
	table.set_col_spacings(5)
	table.attach(Gtk.Label(_('Chose the type of cards:')),0,1,0,1,Gtk.AttachOptions(0),Gtk.AttachOptions(0))
	table.attach(Gtk.Label(_('Speed:')),0,1,1,2,Gtk.AttachOptions(0),Gtk.AttachOptions(0))
	table.attach(Gtk.Label(_('Background:')),0,1,2,3,Gtk.AttachOptions(0),Gtk.AttachOptions(0))
	carte_combo=Gtk.ComboBoxText()
	for tipo in tipi_di_carte:
		carte_combo.append_text(tipo)
	sfondi_combo=Gtk.ComboBoxText()
	for sfondo in sfondi:
		sfondi_combo.append_text(sfondo)
	velocita=Gtk.HScale.new_with_range(1,3,1)
	table.attach(carte_combo,1,2,0,1,Gtk.AttachOptions(4),Gtk.AttachOptions(4))
	table.attach(velocita,1,2,1,2,Gtk.AttachOptions(4),Gtk.AttachOptions(4))
	table.attach(sfondi_combo,1,2,2,3,Gtk.AttachOptions(4),Gtk.AttachOptions(4))
	button=Gtk.Button()
	button.set_label(_('OK'))
	button.connect('pressed',modifica_preferenze,app,carte_combo,velocita,sfondi_combo,win_pre)
	table.attach(button,1,2,4,5,Gtk.AttachOptions(0),Gtk.AttachOptions(0))
	win_pre.add(table)
	carte_combo.set_active(tipi_di_carte.index(settings['cards']))
	sfondi_combo.set_active(sfondi.index(settings['sfondo']))
	velocita.set_value(int(float(settings['speed'])))
	win_pre.show_all()