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

import sys, os
from gi.repository import Gtk,Clutter,GLib
import cairo
import random

APP_VERSION = '0.5'
APP_NAME = 'scopy'

#setting up gettext
import gettext
from gettext import gettext as _
gettext.bindtextdomain('scopy', '/usr/share/locale')
gettext.textdomain('scopy')

#recupero percorsi dove si trovano le immagini
percorso = sys.path[0][0:-4]
percorso_tap = percorso+'/data/images/tappeti/'
percorso_carte = percorso+'/data/images/carte/'
percorso_gui = percorso+'/data/ui/'
percorso_doc = percorso+'/doc/'

#funzione per spostamenti
def go_to(actor,x,y,time):
	an = actor.animatev(Clutter.AnimationMode.EASE_IN_OUT_QUAD, time,['x','y'],[x,y])
	return an

#destroys the given widget
def destroy(widget, response):
	widget.destroy()

def hide_data(event, data):
	data.hide()

#nomi dei file delle immagini delle carte
immagini = [
	["0.png", "1d.png", "2d.png", "3d.png", "4d.png", "5d.png", "6d.png", "7d.png", "8d.png", "9d.png", "10d.png"],
	["bg.png", "1c.png", "2c.png", "3c.png", "4c.png", "5c.png", "6c.png", "7c.png", "8c.png", "9c.png", "10c.png"],
	["mazzo.png", "1b.png", "2b.png", "3b.png", "4b.png", "5b.png", "6b.png", "7b.png", "8b.png", "9b.png", "10b.png"],
	["0.png", "1s.png", "2s.png", "3s.png", "4s.png", "5s.png", "6s.png", "7s.png", "8s.png", "9s.png", "10s.png"]
]

#varianti
varianti = [_('Classic scopa'), _('Cirulla'), _('Cucita'), _('Re Bello')]

#tempo in ms da aspettare dopo che una carta viene giocata, si regola con self.velocita
times=[1,3000,2000,1000]

#caricamento tipi di carte
tipi_di_carte = []
for cartella in os.listdir(percorso_carte):
	if cartella[0] != '.':
		tipi_di_carte.append(cartella)
tipi_di_carte.sort()

#caricamento sfondi
sfondi = []
for cartella in os.listdir(percorso_tap):
	if cartella[0] != '.':
		sfondi.append(cartella[0:-4])
sfondi.sort()

cards='Napoletane'

class Card(Clutter.Texture):
	def __init__(self, suit, value, cards='Napoletane'):
		Clutter.Texture.__init__(self)
		self.suit = suit
		self.value = value
		self.id = 's'+str(suit)+'v'+str(value)
		self.start_x = 0
		self.start_y = 0

	def get_suit():
		return self.suit
		
	def get_value():
		return self.value
	
	def draw_card(self, retro=False):
		if retro:
			self.set_from_file(percorso_carte+cards+'/'+immagini[1][0])
		else:
			self.set_from_file(percorso_carte+cards+'/'+immagini[self.suit][self.value])
	
	def activate(self, play):
		self.set_reactive(True)
		self.connect('button-press-event',play)
		self.connect('enter-event',self.enter)
		self.connect('leave-event',self.leave)
	
	def enter(self, actor, event):
		self.start_x, self.start_y = self.get_x(),self.get_y()
		go_to(self,self.get_x(),self.get_y()-10,100)

	def leave(self, actor, event):
		go_to(self,self.start_x,self.start_y,100)

#container for Card objects, with fixed rows and columns
class Box(Clutter.CairoTexture):
	def __init__(self, rows, cols, spacing=5, child_w=100, child_h=100):
		Clutter.CairoTexture.__init__(self)
		self.set_surface_size(cols*child_w+(cols-1)*spacing,rows*child_h+(rows-1)*spacing)
		self.rows = rows
		self.cols = cols
		self.spacing = spacing
		self.child_w = child_w
		self.child_h = child_h
		self.draw_rect()
		self.children = []
		n=0
		while n<rows:
			self.children.append([])
			i=0
			while i<cols:
				self.children[n].append(0)
				i=i+1
			n=n+1
	
	def get_list(self):
		iterable = []
		for row in self.children:
			for card in row:
				if card != 0:
					iterable.append(card)
		return iterable
		
	def draw_rect(self):
		w,h=self.get_width(),self.get_height()
		self.set_surface_size(w,h)
		self.clear()
		cr = self.create()
		cr.set_source_rgba(1,1,1,0.1)
		cr.move_to(0,0)
		cr.line_to(w,0)
		cr.line_to(w,h)
		cr.line_to(0,h)
		cr.line_to(0,0)
		cr.fill()
		self.invalidate()
	
	def set_children_coords(self):
		n=0
		while n<self.rows:
			i=0
			while i<self.cols:
				if self.children[n][i] != 0:
					 self.children[n][i].set_x(self.x+i*(self.child_w+self.spacing))
					 self.children[n][i].set_y(self.y+n*(self.child_h+self.spacing))
				i=i+1
			n=n+1
	
	def add(self, actor, time=500, add_to_stage=True):
		self.get_allocation_box().get_y()
		r,c=-1,-1
		n=0
		while n<self.rows:
			i=0
			while i<self.cols:
				if self.children[n][i] == 0 and (r,c)==(-1,-1):
					r,c=n,i
					break
				i=i+1
			n=n+1
		self.children[r][c]=actor
		x=self.get_x()+c*(self.child_w+self.spacing)
		y=self.get_y()+r*(self.child_h+self.spacing)
		if add_to_stage:
			stage.add_actor(actor)
		if time != 0:
			go_to(actor,x,y,time)
		else:
			actor.set_position(x,y)
	
	def add_on(self, actor, on_actor, time, add_to_stage=True):
		x=on_actor.get_x()+30
		y=on_actor.get_y()+30
		if add_to_stage:
			stage.add_actor(actor)
		if time != 0:
			go_to(actor,x,y,time)
		else:
			actor.set_position(x,y)
		
	def remove(self, actor):
		n=0
		while n<self.rows:
			i=0
			while i<self.cols:
				if self.children[n][i] == actor:
					self.children[n][i] = 0
				i=i+1
			n=n+1

	def move_to(self, actor, new_box, time=500):
		self.remove(actor)
		new_box.add(actor,time,False)
	
	def move_on(self, actor, on_actor, new_box, time=500):
		self.remove(actor)
		new_box.add_on(actor, on_actor, time, False)
		
	def clean(self):
		n=0
		while n<self.rows:
			i=0
			while i<self.cols:
				self.children[n][i] = 0
				i=i+1
			n=n+1
	
	def hide_all(self):
		for row in range(self.rows):
			for col in range(self.cols):
				if self.children[row][col] != 0:
					self.children[row][col].hide()
		self.hide()
	
	def destroy_all(self):
		for row in range(self.rows):
			for col in range(self.cols):
				if self.children[row][col] != 0:
					self.children[row][col].destroy()
		self.destroy()
	
	def show_all(self):
		for row in range(self.rows):
			for col in range(self.cols):
				if self.children[row][col] != 0:
					self.children[row][col].show()
		self.show()

class Deck(Clutter.CairoTexture):
	def __init__(self, padding=5, child_w=100, child_h=100):
		Clutter.CairoTexture.__init__(self)
		self.set_surface_size(2*padding+child_w+20,2*padding+child_h+20)
		self.connect("allocation-changed",self.draw)
		self.surface = cairo.ImageSurface.create_from_png(percorso_carte+cards+'/'+immagini[1][0])
		self.cards = []
	
	def populate(self):
		for suit in range(4):
			for value in range(1,11):
				self.cards.append(Card(suit, value, cards))
	
	def draw(self, actor_box=0, allocation_flag=0, a=0):
		self.clear()
		c=(len(self.cards)+3)/4
		cr = self.create()
		cr.set_source_rgba(0,0,0,0)
		cr.paint()
		n=0
		while n<c:
			cr.set_source_surface(self.surface,n,n)
			cr.paint()
			n=n+1
		self.invalidate()
	
	def mix(self):
		num_carte = len(self.cards)
		for i in range(num_carte):
			j = random.randrange(0, num_carte)
			self.cards[i], self.cards[j] = self.cards[j], self.cards[i]
	
	def pop(self):
		card = self.cards[0]
		del self.cards[0]
		self.draw()
		return card

	def get_list(self):
		return self.cards
	
	def add(self, actor, time=500, add_to_stage=True):
		self.cards.append(actor)
		y=self.get_allocation_box().get_y()
		x=self.get_x()
		if add_to_stage:
			stage.add_actor(actor)
		if time != 0:
			animation = go_to(actor,x,y,time)
			animation.connect('completed', hide_data, actor)
			animation.connect('completed', self.draw)
		else:
			actor.set_position(x,y)
	
	def reset(self):
		for card in self.cards:
			card.destroy()
		self.cards = []
		self.draw()

#container for clutter actor
class Scope(Clutter.CairoTexture):
	def __init__(self, padding=5, child_w=100, child_h=100):
		Clutter.CairoTexture.__init__(self)
		self.set_surface_size(2*padding+child_w+20,2*padding+child_h+20)
		self.connect("allocation-changed",self.draw)
		self.card = None
		self.scope = 0
	
	def draw(self, actor_box=0, allocation_flag=0, a=0):
		if self.card != None:
			cr = self.create()
			surface = cairo.ImageSurface.create_from_png(percorso_carte+cards+'/'+immagini[self.card.suit][self.card.value])
			cr.set_source_surface(surface,0,0)
			cr.paint()
			self.invalidate()
	
	def add_scopa(self, card, scope=1):
		self.card = card
		self.scope += scope
		self.draw()
	
	def reset(self):
		self.scope=0
		self.card = None
		self.clear()

class NotificationSystem():
	def __init__(self, stage):
		self.stage = stage
		self.mesg = [0,0,0,0]

	def notify(self, messaggio, time):
		sur = cairo.ImageSurface(cairo.FORMAT_ARGB32,500,100)
		tmp = cairo.Context(sur)
		tmp.set_source_rgba(0,0,0,0.5)
		tmp.paint()
		tmp.set_source_rgb(1,1,1)
		tmp.set_font_size(15)
		xb, yb, w, h, xadvance, yadvance = (tmp.text_extents(messaggio))
		tmp.move_to(10,10+h)
		tmp.show_text(messaggio)
		i=0
		while self.mesg[i] != 0:
			i=i+1
		text=Clutter.CairoTexture.new(w+20,h+20)
		text.set_position(self.stage.get_size()[0]-w-30,10+i*(h+30))
		self.stage.add_actor(text)
		self.mesg[i] = text
		cr = text.create()
		cr.set_source_surface(sur,0,0)
		cr.paint()
		text.invalidate()
		if time != 0:
			GLib.timeout_add(time, self.delete, i)
		else:
			return i
	
	#cancella il messaggio con indice 'index'
	def delete(self, index):
		act = self.mesg[index]
		self.mesg[index]=0
		act.destroy()

def destroy_summary(window, event, callback):
	window.destroy()
	callback()

def show_summary(callback, *cols):
	window = Gtk.Dialog()
	window.set_title(_('Game summary'))
	#window.set_transient_for(self.window)
	#window.set_position(Gtk.WindowPosition.CENTER_ON_PARENT)
	window.set_border_width(10)
	window.add_button(_('OK'), 0)
	window.set_default_response(0)
	window.connect('response', destroy_summary, callback)
	box = window.get_content_area()
	hbox=Gtk.HBox()
	box.pack_start(hbox,True,True,5)
	hbox.set_spacing(5)
	for col in cols:
		hbox.pack_start(Gtk.Label(col),True,True,5)
	window.show_all()
	
