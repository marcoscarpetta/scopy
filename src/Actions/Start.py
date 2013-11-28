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
from gi.repository import Gtk,Gio
from libscopyUI import base

Path=_('File')
Name=_('New game...')

class Main():
	def __init__(self, app):
		self.app = app
		self.settings = Gio.Settings.new(base.SCHEMA_ID)
		
		self.dialog = Gtk.Window()

		self.dialog.set_title(_('New game...'))
		self.dialog.set_border_width(10)
		self.dialog.connect('delete-event', base.hide)

		grid=Gtk.Grid()
		grid.set_row_spacing(5)
		grid.set_column_spacing(5)
		self.dialog.add(grid)

		grid.attach(Gtk.Label(_('Name:')),0,0,1,1)
		grid.attach(Gtk.Label(_('Variant:')),0,1,1,1)
		grid.attach(Gtk.Label(_('Number of players:')),0,2,1,1)

		self.name_entry=Gtk.Entry()
		self.var_combo=Gtk.ComboBoxText()
		for variante in base.varianti:
			self.var_combo.append(variante,variante)
		self.n_players=Gtk.ComboBoxText()

		grid.attach(self.name_entry,1,0,1,1)
		grid.attach(self.var_combo,1,1,1,1)
		grid.attach(self.n_players,1,2,1,1)

		self.button=Gtk.Button()
		self.button.set_label(_('Start game!'))
		grid.attach(self.button,1,3,1,1)

		self.name_entry.set_property("activates-default",True)
		self.button.set_can_default(True)
		self.button.grab_default()

		self.dialog.set_transient_for(self.app.window)
		self.dialog.set_position(Gtk.WindowPosition.CENTER_ON_PARENT)
		self.button.connect('pressed',self.start_match)
		self.button.connect('activate',self.start_match)
		self.var_combo.connect('changed',self.set_n_players)
	
	def set_n_players(self, widget=None):
		self.n_players.remove_all()
		for n in base.get_number_of_players(self.var_combo.get_active_id()):
			self.n_players.append(str(n),str(n))
		try:
			self.n_players.set_active_id(str(self.settings.get_int('players')))
		except:
			pass

	def start_match(self, widget=None):
		self.settings.set_string('player-name', self.name_entry.get_text())
		self.settings.set_string('variant', self.var_combo.get_active_id())
		self.settings.set_int('players', int(self.n_players.get_active_id()))
		self.dialog.hide()
		self.app.new_match()

	def main(self, widget=None):
		self.var_combo.set_active_id(self.settings.get_string('variant'))
		self.name_entry.set_text(self.settings.get_string('player-name'))
		self.dialog.show_all()