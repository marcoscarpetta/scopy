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

Path=_('Edit')
Name=_('Settings')

class Main():
	def __init__(self, app):
		self.app = app
		self.dialog = Gtk.Window()
		self.dialog.set_title(_('Edit Settings'))
		self.dialog.set_transient_for(app.window)
		self.dialog.set_position(Gtk.WindowPosition.CENTER_ON_PARENT)
		self.dialog.set_border_width(10)
		self.dialog.connect('delete-event', base.hide)
	
		grid=Gtk.Grid()
		grid.set_row_spacing(5)
		grid.set_column_spacing(5)
		self.dialog.add(grid)
	
		grid.attach(Gtk.Label(_('Chose the type of cards:')),0,0,1,1)
		grid.attach(Gtk.Label(_('Speed:')),0,1,1,1)
		grid.attach(Gtk.Label(_('Background:')),0,2,1,1)
	
		self.carte_combo=Gtk.ComboBoxText()
		for tipo in base.tipi_di_carte:
			self.carte_combo.append_text(tipo)
		self.sfondi_combo=Gtk.ComboBoxText()
		for sfondo in base.sfondi:
			self.sfondi_combo.append_text(sfondo)
		self.velocita=Gtk.HScale.new_with_range(1,3,1)
	
		grid.attach(self.carte_combo,1,0,1,1)
		grid.attach(self.velocita,1,1,1,1)
		grid.attach(self.sfondi_combo,1,2,1,1)
	
		button=Gtk.Button()
		button.set_label(_('OK'))
		button.connect('pressed', self.modifica_preferenze)
		grid.attach(button,1,3,1,1)
	
		self.carte_combo.set_active(base.tipi_di_carte.index(self.app.settings['cards']))
		self.sfondi_combo.set_active(base.sfondi.index(self.app.settings['sfondo']))
		self.velocita.set_value(int(float(self.app.settings['speed'])))
		
	#modifica le preferenze in base ai valori dati dall'utente
	def modifica_preferenze(self, widget):
		if self.app.settings['cards'] != base.tipi_di_carte[self.carte_combo.get_active()]:
			self.app.settings['cards'] = base.tipi_di_carte[self.carte_combo.get_active()]
			if self.app.partita:
				self.app.partita.update_cards()
		self.app.settings['speed']=self.velocita.get_value()
		self.app.settings['sfondo']=base.sfondi[self.sfondi_combo.get_active()]
		self.app.back_img.set_from_file(base.percorso_tap+self.app.settings['sfondo']+'.png')
		self.app.settings.save()
		self.dialog.hide()

	def main(self, widget):
		self.dialog.show_all()