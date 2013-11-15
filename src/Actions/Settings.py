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

Path=_('Edit')
Name=_('Settings')

class Main():
	def __init__(self, app):
		self.app = app
		self.settings = Gio.Settings.new(base.SCHEMA_ID)
		
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
		grid.attach(Gtk.Label(_('Show value on cards:')),0,3,1,1)
	
		self.cards_combo = Gtk.ComboBoxText()
		for tipo in base.tipi_di_carte:
			self.cards_combo.append_text(tipo)
		self.cards_combo.connect("changed", self.on_cards_combo_changed)
		
		self.back_button = Gtk.Button()
		self.image = Gtk.Image.new()
		self.load_image()
		self.back_button.set_image(self.image)
		self.back_button.connect('pressed', self.on_back_button_pressed)
		self.back_dialog = Gtk.FileChooserDialog(_("Select background image"),
			self.dialog,
			Gtk.FileChooserAction.OPEN,
			(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
			Gtk.STOCK_OPEN, Gtk.ResponseType.ACCEPT))
		self.back_dialog.add_shortcut_folder(base.percorso_tap)
		self.back_dialog.connect('response', self.on_back_dialog_response)
		self.back_dialog.connect('update-preview', self.on_back_dialog_update_preview)
		self.back_dialog.connect('delete-event', self.on_back_button_pressed)
		file_filter = Gtk.FileFilter()
		file_filter.set_name(_('Image files'))
		file_filter.add_pixbuf_formats()
		self.back_dialog.add_filter(file_filter)
		
		self.speed_scale=Gtk.Scale.new_with_range(Gtk.Orientation.HORIZONTAL, 1, 3, 1)
		
		self.show_value_on_cards = Gtk.Switch()
		self.show_value_on_cards.set_active(self.settings.get_boolean('show-value-on-cards'))
		self.show_value_on_cards.connect("notify::active", self.on_show_value_on_cards_changed)
	
		grid.attach(self.cards_combo,1,0,1,1)
		grid.attach(self.speed_scale,1,1,1,1)
		grid.attach(self.back_button,1,2,1,1)
		grid.attach(self.show_value_on_cards,1,3,1,1)
	
		button=Gtk.Button()
		button.set_label(_('OK'))
		button.connect('pressed', self.modifica_preferenze)
		grid.attach(button,1,4,1,1)
	
		self.cards_combo.set_active(base.tipi_di_carte.index(self.settings.get_string('cards')))
		self.speed_scale.set_value(self.settings.get_int('speed'))
	
	def on_back_button_pressed(self, event):
		self.back_dialog.run()
	
	def on_back_dialog_response(self, event, response_id=0):
		if response_id == -3:
			self.settings.set_string('background', self.back_dialog.get_filename())
			self.load_image()
		self.back_dialog.hide()
		return True
	
	def on_back_dialog_update_preview(self, widget):
		if self.back_dialog.get_preview_filename():
			self.settings.set_string('background', self.back_dialog.get_preview_filename())
			self.app.table.set_from_file(self.back_dialog.get_preview_filename())

	def load_image(self):
		tmp = Gtk.Image.new_from_file(self.settings.get_string('background'))
		pixbuf = tmp.get_pixbuf()
		w = 200
		h = pixbuf.get_height()*w/pixbuf.get_width()
		pixbuf = pixbuf.scale_simple(w, h, 1)
		self.image.set_from_pixbuf(pixbuf)

	def on_cards_combo_changed(self, widget):
		self.settings.set_string('cards', base.tipi_di_carte[self.cards_combo.get_active()])
	
	def on_show_value_on_cards_changed(self, widget, data):
		self.settings.set_boolean('show-value-on-cards', self.show_value_on_cards.get_active())
	
	#modifica le preferenze in base ai valori dati dall'utente
	def modifica_preferenze(self, widget):
		self.settings.set_int('speed', self.speed_scale.get_value())
		self.app.table.set_from_file(self.settings.get_string('background'))
		self.dialog.hide()

	def main(self, widget):
		self.dialog.show_all()