#!/usr/bin/python
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

from libscopyUI import MenuCreator
from libscopyUI import base
from Actions import Start
from gi.repository import Gtk,Gdk,GtkClutter,Clutter
from gettext import gettext as _
import cairo
GtkClutter.init([])

#classe che contiene tutti i metodi necessari alla creazione e funzionamento della gui
class Application():
	def __init__(self):
		#main window
		self.window = Gtk.Window()
		self.window.connect('delete-event', Gtk.main_quit)
		self.window.set_position(Gtk.WindowPosition.CENTER)
		self.window.maximize()

		#main window widgets
		grid = Gtk.Grid()
		self.embed = GtkClutter.Embed.new()
		self.stage = self.embed.get_stage()
		base.stage = self.stage
		grid.attach(self.embed, 0, 1, 1, 1)
		self.status_bar = Gtk.Statusbar()
		grid.attach(self.status_bar, 0, 3, 1, 3)
		menu, classes=MenuCreator.create_menu(self)
		grid.attach(menu, 0, 0, 3, 1)
		self.window.add(grid)
		
		#icon
		icon = cairo.ImageSurface.create_from_png(base.percorso+'/data/icons/icona32.png')
		pixbuf = Gdk.pixbuf_get_from_surface(icon,0,0,icon.get_width(),icon.get_height())
		self.window.set_icon(pixbuf)
				
		#background
		self.actor = Clutter.Actor()
		self.back_img = Clutter.Texture.new_from_file(base.percorso_tap+base.settings['sfondo']+'.png')
		self.back_img.set_repeat(True,True)
		self.grid = Clutter.TableLayout()
		self.grid.set_row_spacing(10)
		self.grid.set_column_spacing(10)
		self.actor.set_layout_manager(self.grid)
		self.stage.add_actor(self.back_img)
		self.stage.add_actor(self.actor)
		self.actor.connect('notify::allocation',self.window_resized)
		
		#title
		self.window.set_title(_('ScoPy'))

		#alcune variabili di controllo
		self.start_function = classes[_('New game...')].main
		self.time = base.times[int(float(base.settings['speed']))]
		self.partita = None
		self.window.show_all()

	#controlla che lo sfondo copra tutta la finestra
	def window_resized(self,widget=None,event=None,a=0):
		#self.window.resize(self.actor.get_width(),self.actor.get_height())
		self.width, self.height = self.embed.get_allocated_width(), self.embed.get_allocated_height()
		self.back_img.set_size(self.width, self.height)
		
	def update_status_bar(self, text):
		c_id = self.status_bar.get_context_id('situazione')
		self.status_bar.push(c_id, text)

	#crea una nuova partita in base ai dati in self.opzioni
	def nuova_partita(self):
		if self.partita != None:
			self.partita.destroy()
		self.partita = base.create_match(self.grid,self.stage,self.start_function,self.update_status_bar)
		self.partita.start()


app = Application()
app.start_function(None)
Gtk.main()