#!/usr/bin/python
# coding: utf-8

##
# Project: ScoPy - The italian card game 'scopa'
# Author: Marco Scarpetta <marcoscarpetta@mailoo.org>
# Copyright: 2011-2014 Marco Scarpetta
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

import os
import webbrowser
from libscopyUI import base,widgets
from gi.repository import Gtk,GtkClutter,Gio,GLib
from gettext import gettext as _
GtkClutter.init([])

class Application():
	def __init__(self):
		#application settings
		self.settings = Gio.Settings.new(base.SCHEMA_ID)
		
		#builder
		self.builder = Gtk.Builder.new_from_file(base.percorso+"/data/ui/ui.glade")
		self.builder.connect_signals(self)
		
		#main window
		self.mainWindow = self.builder.get_object("main-window")
		self.mainWindow.connect("delete-event", self.quit)
		self.mainWindow.set_position(Gtk.WindowPosition.CENTER)
		self.mainWindow.resize(*self.settings.get_value("window-size"))

		#main window widgets
		self.embed = GtkClutter.Embed.new()
		self.embed.connect('configure-event', self.window_resized)
		self.stage = self.embed.get_stage()
		base.stage = self.stage
		self.builder.get_object("grid1").attach(self.embed, 0, 1, 1, 1)
				
		#background
		self.table = widgets.Table()
		self.table.set_on_child_added_callback(self._set_size_request)
		self.table.set_from_file(self.settings.get_string('background'))
		self.table.set_repeat(True,True)
		self.stage.add_actor(self.table)
		
		#alcune variabili di controllo
		self.match = None
		
		#loading variants in new game window
		self.variants_combo = self.builder.get_object("variants-combo")
		for variant in base.variants:
			self.variants_combo.append(variant, variant)
		
		#loading settings window initial values
		self.cards_combo = self.builder.get_object("cards-combo")
		for cards_type in base.cards_types:
			self.cards_combo.append_text(cards_type)
		
		self.builder.get_object("values-on-card-switch").set_active(
			self.settings.get_boolean('show-value-on-cards'))
		
		back_button = self.builder.get_object("background-button")
		self.image = Gtk.Image.new()
		self.load_image()
		back_button.set_image(self.image)
		self.background_dialog = Gtk.FileChooserDialog(_("Select background image"),
			self.builder.get_object("settings-window"),
			Gtk.FileChooserAction.OPEN,
			(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
			Gtk.STOCK_OPEN, Gtk.ResponseType.ACCEPT))
		self.background_dialog.add_shortcut_folder(base.percorso_tap)
		self.background_dialog.connect('response', self.on_back_dialog_response)
		self.background_dialog.connect('update-preview', self.on_back_dialog_update_preview)
		self.background_dialog.connect('delete-event', self.background_button_clicked)
		file_filter = Gtk.FileFilter()
		file_filter.set_name(_('Image files'))
		file_filter.add_pixbuf_formats()
		self.background_dialog.add_filter(file_filter)
		
		self.cards_combo.set_active(base.cards_types.index(self.settings.get_string('cards')))
		self.builder.get_object("speed-button").set_value(self.settings.get_int('speed'))
		
		self.mainWindow.show_all()

	def _set_size_request(self):
		self.embed.set_size_request(*self.table.get_min_size())

	#controlla che lo sfondo copra tutta la finestra
	def window_resized(self,widget=None,event=None,a=0):
		width, height = self.embed.get_allocated_width(), self.embed.get_allocated_height()
		self.table.set_size(width, height)
		self.settings.set_value("window-size", GLib.Variant('(ii)',self.mainWindow.get_size()))
		
	def update_status_bar(self, text):
		statusbar = self.builder.get_object("statusbar")
		c_id = statusbar.get_context_id('situazione')
		statusbar.push(c_id, text)

	def new_match(self):
		if self.match != None:
			self.match.destroy()
		self.match = base.create_match(self)
		self.match.start()
	
	### New game window
	def set_number_of_players(self, widget=None):
		combo = self.builder.get_object("number-of-players-combo")
		combo.remove_all()
		for n in base.get_number_of_players(self.variants_combo.get_active_id()):
			combo.append(str(n), str(n))
		try:
			combo.set_active_id(str(self.settings.get_int('players')))
		except:
			pass
	
	def new_game_menu_item_activate(self, widget=None):
		self.variants_combo.set_active_id(self.settings.get_string('variant'))
		self.builder.get_object("name-entry").set_text(self.settings.get_string('player-name'))
		self.builder.get_object("new-game-window").show()
	
	def start_game_button_clicked(self, widget=None):
		self.settings.set_string('player-name', self.builder.get_object("name-entry").get_text())
		self.settings.set_string('variant', self.variants_combo.get_active_id())
		self.settings.set_int('players', int(self.builder.get_object("number-of-players-combo").get_active_id()))
		self.builder.get_object("new-game-window").hide()
		self.new_match()
	
	### Settings window
	def settings_menu_item_activate(self, widget=None):
		self.builder.get_object("settings-window").show()
	
	def background_button_clicked(self, widget):
		self.background_dialog.run()
	
	def on_back_dialog_response(self, event, response_id=0):
		if response_id == -3:
			self.settings.set_string('background', self.background_dialog.get_filename())
			self.load_image()
		self.background_dialog.hide()
		return True
	
	def on_back_dialog_update_preview(self, widget):
		if self.background_dialog.get_preview_filename():
			self.settings.set_string('background', self.background_dialog.get_preview_filename())
			self.table.set_from_file(self.background_dialog.get_preview_filename())

	def load_image(self):
		tmp = Gtk.Image.new_from_file(self.settings.get_string('background'))
		pixbuf = tmp.get_pixbuf()
		w = 200
		h = pixbuf.get_height()*w/pixbuf.get_width()
		pixbuf = pixbuf.scale_simple(w, h, 1)
		self.image.set_from_pixbuf(pixbuf)

	def cards_combo_changed(self, widget):
		self.settings.set_string('cards', base.cards_types[self.cards_combo.get_active()])
	
	def values_on_cards_activate(self, widget, data):
		self.settings.set_boolean(
			'show-value-on-cards', self.builder.get_object("values-on-card-switch").get_active())
	
	def settings_ok_button_clicked(self, widget):
		self.settings.set_int('speed', self.builder.get_object("speed-button").get_value())
		self.table.set_from_file(self.settings.get_string('background'))
		self.builder.get_object("settings-window").hide()
	
	### Last move
	def hide_last_move(self, actor, event, widget, args):
		self.match.hide_last_move(None,None,*args)
		if widget == None: widget=self.widget
		widget.set_label(_('Show last move'))
		widget.disconnect_by_func(self.hide_last_move)
		widget.connect('activate', self.show_last_move)

	def show_last_move(self, widget):
		self.widget = widget
		args = self.match.show_last_move()
		if args:
			widget.set_label(_('Hide last move'))
			widget.disconnect_by_func(self.show_last_move)
			widget.connect('activate', self.hide_last_move, None, widget, args)
	
	### Help
	def get_path(self):
		try:
			lang = os.environ['LANG'][0:2]
		except:
			lang = 'en'
		if os.path.exists(base.percorso_doc+lang+'/index.html'):
			return 'file://'+base.percorso_doc+lang+'/index.html'
		else:
			return 'file://'+base.percorso_doc+'en/index.html'
	
	def help_menu_item_activate(self, widget):
		webbrowser.open(self.get_path(),2,True)
	
	### About window
	def about_menu_item_activate(self, widget):
		self.builder.get_object("about-dialog").show()
	
	### Hides 'widget'
	def hide(self, widget, *data):
		widget.hide()
		return True
	
	def quit(self, *data):
		Gtk.main_quit()

app = Application()
app.new_game_menu_item_activate(None)
Gtk.main()
