#!/usr/bin/python
# coding: utf-8

##
# Project: ScoPy - The italian card game 'scopa'
# Author: Marco Scarpetta <marcoscarpetta02@gmail.com>
# Copyright: 2011-2012 Marco Scarpetta
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
from libscopyUI.base import *
from libscopyUI import base
from Actions import Start
from gi.repository import GLib,Gtk,Gdk,GtkClutter,Clutter
from gettext import gettext as _
import cairo
import sys,os
import pickle
GtkClutter.init([])

#classe che contiene tutti i metodi necessari alla creazione e funzionamento della gui
class main_win():
	def __init__(self):
		#carica le opzioni
		self.default = {
			'nome':_('Player'),
			'variante':_('Classic scopa'),
			'speed':'3',
			'carte':'Napoletane',
			'sfondo':'verde',
			}
		self.load_opzioni()
		#impostazioni finestra principale
		self.window = Gtk.Window()
		self.window.connect('delete-event', Gtk.main_quit)
		self.window.set_position(Gtk.WindowPosition.CENTER)
		self.window.maximize()
		table = Gtk.Table(3, 3, False)
		self.embed = GtkClutter.Embed.new()
		self.stage = self.embed.get_stage()
		base.stage = self.stage
		table.attach(self.embed, 1, 2, 1, 2)
		#immagine sfondo
		self.actor = Clutter.Actor()
		self.back_img = Clutter.Texture.new_from_file(percorso_tap+self.opzioni['sfondo']+'.png')
		self.back_img.set_repeat(True,True)
		self.grid = Clutter.TableLayout()
		self.grid.set_row_spacing(10)
		self.grid.set_column_spacing(10)
		self.actor.set_layout_manager(self.grid)
		self.stage.add_actor(self.back_img)
		self.stage.add_actor(self.actor)
		self.actor.connect('notify::allocation',self.window_resized)
		#icona
		icon = cairo.ImageSurface.create_from_png(percorso+'/data/icons/icona32.png')
		pixbuf = Gdk.pixbuf_get_from_surface(icon,0,0,icon.get_width(),icon.get_height())
		self.window.set_icon(pixbuf)
		#titolo
		self.window.set_title(_('ScoPy'))
		self.status_bar = Gtk.Statusbar()
		self.vbox = Gtk.VBox()
		table.attach(self.status_bar,0,3,3,4,Gtk.AttachOptions(4),Gtk.AttachOptions(4))
		table.attach(self.vbox,0,3,0,1,Gtk.AttachOptions(4),Gtk.AttachOptions(4))
		self.window.add(table)
		#alcune variabili di controllo 
		self.time = times[int(float(self.opzioni['speed']))]
		self.partita = None
		#creazione menu
		menu=MenuCreator.create_menu(self)
		self.vbox.pack_start(menu,True,True,0)
		self.window.show_all()
	#modifica le posizioni dei boxes quando si modifica il tipo di carte
	def carte_modificate(self):
		actor = Clutter.Texture.new_from_file(percorso_carte+self.opzioni['carte']+'/'+immagini[1][0])
		w = actor.get_width()
		h = actor.get_height()
		for box in self.boxes:
			self.boxes[box].set_child_size(w,h)
		self.boxes['prese_c'].set_retro(percorso_carte+self.opzioni['carte']+'/'+immagini[1][0])
		self.boxes['prese_g'].set_retro(percorso_carte+self.opzioni['carte']+'/'+immagini[1][0])
		self.boxes['scope_c'].set_scopa(percorso_carte+self.opzioni['carte']+'/'+immagini[self.partita.giocatore[1].ult_scopa[0]][self.partita.giocatore[1].ult_scopa[1]])
		self.boxes['scope_g'].set_scopa(percorso_carte+self.opzioni['carte']+'/'+immagini[self.partita.giocatore[0].ult_scopa[0]][self.partita.giocatore[0].ult_scopa[1]])
		width=self.boxes['terra'].get_width()+self.boxes['prese_c'].get_width()+self.boxes['scope_c'].get_width()
		height=self.boxes['computer'].get_height()+self.boxes['terra'].get_height()+self.boxes['giocatore'].get_height()
		self.embed.set_size_request(width, height)
	#controlla che lo sfondo copra tutta la finestra
	def window_resized(self,widget=None,event=None,a=0):
		#self.window.resize(self.actor.get_width(),self.actor.get_height())
		self.width, self.height = self.embed.get_allocated_width(), self.embed.get_allocated_height()
		self.back_img.set_size(self.width, self.height)

	#nasconde 'widget'
	def hide(self, widget, data=None):
		widget.hide()
		return True

	#nasconde 'data'
	def hide_d(self, widget, data):
		data.hide()

	#funzioni per il salvataggio e caricamento delle opzioni
	def load_opzioni(self):
		d = os.path.expanduser('~')+"/.scopy"
		if not os.path.exists(d):
			os.makedirs(d)
			config = open(os.path.expanduser('~')+"/.scopy/config", 'w')
			config.close()
			self.opzioni = {}
			for key in self.default:
				self.opzioni[key] = self.default[key]
			self.save()
		else:
			try:
				self.opzioni = self.parse(os.path.expanduser('~')+"/.scopy/config")
				for key in self.default:
					if not key in self.opzioni:
						self.opzioni[key] = self.default[key]
				if self.opzioni['variante'] not in varianti:
					self.opzioni['variante'] = self.default['variante']
				self.save()
			except:
				self.opzioni = {}
				for key in self.default:
					self.opzioni[key] = self.default[key]
				self.save()
	def save(self):
		config = open(os.path.expanduser('~')+"/.scopy/config", 'w')
		for key in self.opzioni:
			config.write(key+'='+self.opzioni[key]+'\n')
		config.close()
	def parse(self, file_name):
		lang = {}
		f = open(file_name)
		riga = f.readline()
		while riga != '':
			try:
				pos_uguale = riga.index('=')
			except:
				break
			lang[riga[0:pos_uguale]]=riga[pos_uguale+1:-1]
			riga = f.readline()
		return lang

	#crea una nuova partita in base ai dati in self.opzioni
	def crea_partita(self, nc=None):
		if nc==None:
			nc=_('Computer')
		if self.partita != None:
			self.partita.destroy()
		if self.opzioni['variante'] == None:
			from libscopy import classica
			self.partita = classica.partita(self.opzioni['nome'],nc)
		if self.opzioni['variante'] == _('Classic scopa'):
			from libscopy import core
			self.partita = core.Partita(self.grid, self.stage, (self.opzioni['nome'],nc), self.show_start_win)
		if self.opzioni['variante'] == _('Cirulla'):
			from libscopy import cirulla
			self.partita = cirulla.partita(self.opzioni['nome'],nc)
		if self.opzioni['variante'] == _('Cucita'):
			from libscopy import cucita
			self.partita = cucita.partita(self.opzioni['nome'],nc)
		if self.opzioni['variante'] == _('Re Bello'):
			from libscopy import re_bello
			self.partita = re_bello.partita(self.opzioni['nome'],nc)
	
	def show_start_win(self):
		Start.main(None, self)

main_win = main_win()
main_win.show_start_win()
Gtk.main()