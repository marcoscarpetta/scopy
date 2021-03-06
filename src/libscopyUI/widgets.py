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

from gi.repository import Gtk,Clutter,GLib,Gio
from libscopyUI import base
import cairo
import random
from gettext import gettext as _

min_width = 30
min_height = 1
#card's shadow parameters
s=10
r=10

#funzione per spostamenti
def go_to(actor,x,y,time):
	an = actor.animatev(Clutter.AnimationMode.EASE_IN_OUT_QUAD, time,['x','y'],[x,y])
	return an

class Table(Clutter.Texture):
	def __init__(self, spacing=10):
		Clutter.CairoTexture.__init__(self)
		self._children = []
		self._children_rows = []
		self._children_columns = []
		self._rows = 0
		self._columns = 0
		self._on_child_added = None
		self._spacing = spacing
		#self._g_sources_id = []
	
	def set_on_child_added_callback(self, callback):
		self._on_child_added = callback
	
	def relayout(self):
		self_width = self.get_width()-(self._columns-1)*self._spacing
		self_height = self.get_height()-(self._rows-1)*self._spacing
		max_width = [0]*self._columns
		max_height = [0]*self._rows
		i=0
		while i <len(self._children):
			max_width[self._children_columns[i]] = max(max_width[self._children_columns[i]], self._children[i].get_natural_width())
			max_height[self._children_rows[i]] = max(max_height[self._children_rows[i]], self._children[i].get_natural_height())
			i+=1
		reducible_columns = []
		for c in range(self._columns):
			reducibles = []
			natural_width, min_width = 0,0
			for i in range(len(self._children)):
				if self._children_columns[i] == c:
					min_width = max(min_width, self._children[i].get_min_width())
					natural_width = max(natural_width, self._children[i].get_natural_width())
					if self._children[i].get_min_width()<self._children[i].get_natural_width():
						reducibles.append(self._children[i])
			if min_width < natural_width:
				reducible_columns.append([min_width, natural_width, reducibles])
		for column in reducible_columns:
			new_width = column[1]-(sum(max_width)-self_width)/len(reducible_columns)
			for actor in column[2]:
				actor.set_max_width(new_width)
		reducible_rows = []
		for r in range(self._rows):
			reducibles = []
			natural_height, min_height = 0,0
			for i in range(len(self._children)):
				if self._children_rows[i] == r:
					min_height = max(min_height, self._children[i].get_min_height())
					natural_height = max(natural_height, self._children[i].get_natural_height())
					if self._children[i].get_min_height()<self._children[i].get_natural_height():
						reducibles.append(self._children[i])
			if min_height < natural_height:
				reducible_rows.append([min_height, natural_height, reducibles])
		for row in reducible_rows:
			new_height = row[1]-(sum(max_height)-self_height)/len(reducible_rows)
			for actor in row[2]:
				actor.set_max_height(new_height)
		max_width = [0]*self._columns
		max_height = [0]*self._rows
		i=0
		while i <len(self._children):
			max_width[self._children_columns[i]] = max(max_width[self._children_columns[i]], self._children[i].get_width())
			max_height[self._children_rows[i]] = max(max_height[self._children_rows[i]], self._children[i].get_height())
			i+=1
		freex, freey = 0,0
		if self._columns>1 and self.get_width()>sum(max_width):
			freex=int((self_width-sum(max_width))/(self._columns-1))
		if self._rows>1 and self.get_height()>sum(max_height):
			freey=int((self_height-sum(max_height))/(self._rows-1))
		i=0
		while i <len(self._children):
			cx=int((max_width[self._children_columns[i]]-self._children[i].get_width())/2)+freex*self._children_columns[i]
			cy=int((max_height[self._children_rows[i]]-self._children[i].get_height())/2)+freey*self._children_rows[i]
			x=sum(max_width[:self._children_columns[i]])+self._children_columns[i]*self._spacing+cx
			y=sum(max_height[:self._children_rows[i]])+self._children_rows[i]*self._spacing+cy
			self._children[i].set_position(x,y)
			i+=1
	
	def set_size(self, width, height):
		Clutter.Actor.set_size(self, width, height)
		self.relayout()

	def pack(self, actor, column, row):
		i=0
		while i<len(self._children):
			if self._children_rows[i] == row and self._children_columns[i] == column:
				raise Exception('There is yet an actor on that place')
			i+=1
		self.get_parent().add_actor(actor)
		self._children.append(actor)
		self._children_rows.append(row)
		self._children_columns.append(column)
		self._rows = max(self._rows, row+1)
		self._columns = max(self._columns, column+1)
		self.relayout()
		if self._on_child_added:
			self._on_child_added()
	
	def get_min_size(self):
		max_width = [0]*self._columns
		max_height = [0]*self._rows
		i=0
		while i <len(self._children):
			max_width[self._children_columns[i]] = max(max_width[self._children_columns[i]], self._children[i].get_min_width())
			max_height[self._children_rows[i]] = max(max_height[self._children_rows[i]], self._children[i].get_min_height())
			i+=1
		return (sum(max_width)+(self._columns-1)*self._spacing,sum(max_height)+(self._rows-1)*self._spacing)
	
	def timeout_add(self, interval, function, *data):
		ID = GLib.timeout_add(interval, function, *data)
		#self._g_sources_id.append(ID)
	
	def destroy_all_children(self):
		#for source_id in self._g_sources_id:
		#	GLib.Source.remove(source_id)
		for children in self._children:
			children.destroy()
		for child in self.get_stage().get_children():
			if child != self:
				child.destroy()
		self._children = []
		self._children_rows = []
		self._children_columns = []
		self._rows = 0
		self._columns = 0

#Clutter actor that showing a card
class Card(Clutter.Actor):
	def __init__(self, suit, value):
		Clutter.Actor.__init__(self)
		self.settings = Gio.Settings.new(base.SCHEMA_ID)
		self.suit = suit
		self.value = value
		self.mouse_over = False
		self.face_up = False
		self.canvas = Clutter.Canvas()
		self.canvas.connect("draw", self._draw)
		self.set_content(self.canvas)
		self.w = 0
		self.h = 0

	def get_suit(self):
		return self.suit
		
	def get_value(self):
		return self.value
	
	def draw_card(self, face_up=True):
		self.face_up = face_up
		self.w, self.h=base.get_card_size()
		if self.get_reactive():
			flag = self.canvas.set_size(self.w+s,self.h+s)
			self.set_size(self.w+s,self.h+s)
		else:
			flag = self.canvas.set_size(self.w,self.h)
			self.set_size(self.w,self.h)
		if (not flag): self.canvas.invalidate()
		
	def _draw(self, canvas, cr, width, height):
		cr.set_operator(cairo.OPERATOR_CLEAR)
		cr.paint()
		cr.set_operator(cairo.OPERATOR_OVER)
		w,h=base.get_card_size()
		if self.face_up:
			### Shadow effect using cairo, clutter one doesn't work ###
			if self.mouse_over:
				#down-left corner
				rg = cairo.RadialGradient(s+r, self.h-r, 0, s+r, self.h-r, s+r)
				rg.add_color_stop_rgba(0.0, 0.4, 0.4, 0.4, 1.0)
				rg.add_color_stop_rgba(1.0, 0, 0, 0, 0)  
				cr.set_source(rg)
				cr.rectangle(0, self.h-r, s+r, s+r)
				cr.fill()
				#down
				lg = cairo.LinearGradient(0, self.h-r, 0, self.h+s)
				lg.add_color_stop_rgba(0.0, 0.4, 0.4, 0.4, 1.0)
				lg.add_color_stop_rgba(1.0, 0, 0, 0, 0)    
				cr.rectangle(s+r, self.h-r, self.w-s-2*r, s+r)
				cr.set_source(lg)
				cr.fill()
				#top-right corner
				rg = cairo.RadialGradient(self.w-r, s+r, 0, self.w-r, s+r, s+r)
				rg.add_color_stop_rgba(0.0, 0.4, 0.4, 0.4, 1.0)
				rg.add_color_stop_rgba(1.0, 0, 0, 0, 0)  
				cr.set_source(rg)
				cr.rectangle(self.w-r, 0, s+r, s+r)
				cr.fill()
				#up
				lg = cairo.LinearGradient(self.w-r, 0, self.w+s, 0)
				lg.add_color_stop_rgba(0.0, 0.4, 0.4, 0.4, 1.0)
				lg.add_color_stop_rgba(1.0, 0, 0, 0, 0)    
				cr.rectangle(self.w-r, s+r, self.w+r, self.h-s-2*r)
				cr.set_source(lg)
				cr.fill()
				#down-right corner
				rg = cairo.RadialGradient(self.w-r, self.h-r, 0, self.w-r, self.h-r, s+r)
				rg.add_color_stop_rgba(0.0, 0.4, 0.4, 0.4, 1.0)
				rg.add_color_stop_rgba(1.0, 0, 0, 0, 0)  
				cr.set_source(rg)
				cr.rectangle(self.w-r, self.h-r, s+r, s+r)
				cr.fill()
			### Now drawing the card ### 
			surface = cairo.ImageSurface.create_from_png(base.percorso_carte+self.settings.get_string('cards')+'/'+base.immagini[self.suit][self.value])
			cr.set_source_surface(surface,0,0)
			cr.paint()
			if self.settings.get_boolean('show-value-on-cards'):
				cr.set_font_size(15)
				xb, yb, w, h, xadvance, yadvance = (cr.text_extents(str(self.value)))
				w,h=int(w),int(h)
				sur = cairo.ImageSurface(cairo.FORMAT_ARGB32,w+10,h+10)
				tmp = cairo.Context(sur)
				tmp.set_source_rgb(0,0,0)
				tmp.paint()
				tmp.set_source_rgb(1,1,1)
				tmp.set_font_size(15)
				tmp.move_to(5,h+5)
				tmp.show_text(str(self.value))
				cr.set_source_surface(sur,0,0)
				cr.paint()
		else:
			surface = cairo.ImageSurface.create_from_png(base.percorso_carte+self.settings.get_string('cards')+'/'+base.immagini[1][0])
			cr.set_source_surface(surface,0,0)
			cr.paint()
		return True

	def activate(self, play):
		self.set_reactive(True)
		self.connect('button-press-event',play)
		self.connect('button-press-event',self.leave)
		self.connect('enter-event',self.enter)
		self.connect('leave-event',self.leave)
	
	def enter(self, actor, event):
		self.mouse_over = True
		self.draw_card()

	def leave(self, actor, event):
		self.mouse_over = False
		self.draw_card()

#container for Card objects, with fixed number of rows and columns
class Box(Clutter.Actor):
	def __init__(self, app, rows, cols, spacing=15):
		Clutter.Actor.__init__(self)
		self.settings = Gio.Settings.new(base.SCHEMA_ID)
		self.settings.connect("changed::cards", self.update_cards)
		self.settings.connect("changed::show-value-on-cards", self.update_cards)
		self.app = app
		self.canvas = Clutter.Canvas()
		self.canvas.connect("draw", self.draw_rect)
		self.set_content(self.canvas)
		self.set_x_expand(False)
		self.set_y_expand(False)
		self.column_width, self.row_height = base.get_card_size()
		self.canvas.set_size(cols*self.column_width+(cols+1)*spacing,rows*self.row_height+(rows+1)*spacing)
		self.max_height = 0
		self.max_width = 0
		self.rows = rows
		self.cols = cols
		self.face_up = True
		self.spacing = spacing
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
		
	def draw_rect(self, canvas, cr, width, height):
		self.set_size(width,height)
		cr.set_operator(cairo.OPERATOR_CLEAR)
		cr.paint()
		cr.set_operator(cairo.OPERATOR_OVER)
		cr.set_source_rgba(1,1,1,0.1)
		cr.move_to(0,0)
		cr.line_to(width,0)
		cr.line_to(width,height)
		cr.line_to(0,height)
		cr.line_to(0,0)
		cr.fill()
		return True
	
	def relayout(self):
		card_w,card_h = base.get_card_size()
		if self.max_height>0 and self.rows>1:
			self.row_height = int((self.max_height-(self.rows+1)*self.spacing-card_h)/(self.rows-1))
		if self.max_width>0 and self.cols>1:
			self.column_width = int((self.max_width-(self.cols+1)*self.spacing-card_w)/(self.cols-1))
		h=(self.rows+1)*self.spacing+card_h+(self.rows-1)*self.row_height
		w=(self.cols+1)*self.spacing+card_w+(self.cols-1)*self.column_width
		self.canvas.set_size(w,h)
		r=0
		while r<self.rows:
			c=0
			while c<self.cols:
				if self.children[r][c] != 0:
					 self.children[r][c].set_x(self.get_x()+c*(self.column_width+self.spacing)+self.spacing)
					 self.children[r][c].set_y(self.get_y()+r*(self.row_height+self.spacing)+self.spacing)
				c+=1
			r+=1
	
	def set_face_up(self, face_up):
		self.face_up = face_up
		self.redraw_cards()
	
	def get_face_up(self):
		return self.face_up
	
	def redraw_cards(self):
		for card in self.get_list():
			card.draw_card(self.face_up)
	
	def update_cards(self, settings, key):
		self.redraw_cards()
		self.relayout()
	
	def set_position(self, x, y):
		Clutter.Actor.set_position(self, x, y)
		self.relayout()

	def get_min_width(self):
		if self.cols>1:
			return (self.cols+1)*self.spacing+(self.cols-1)*min_width+base.get_card_size()[0]
		return (self.cols+1)*self.spacing+self.cols*base.get_card_size()[0]
	
	def get_min_height(self):
		if self.rows>1:
			return (self.rows+1)*self.spacing+(self.rows-1)*min_height+base.get_card_size()[1]
		return (self.rows+1)*self.spacing+self.rows*base.get_card_size()[1]
		
	def get_natural_width(self):
		return (self.cols+1)*self.spacing+self.cols*base.get_card_size()[0]
	
	def get_natural_height(self):
		return (self.rows+1)*self.spacing+self.rows*base.get_card_size()[1]
	
	def set_max_height(self, height):
		if height > self.get_natural_height():
			self.max_height = self.get_natural_height()
		else:
			self.max_height = height
		self.relayout()
	
	def set_max_width(self, width):
		if width > self.get_natural_width():
			self.max_width = self.get_natural_width()
		else:
			self.max_width = width
		self.relayout()

	def add(self, actor, time=500, add_to_stage=True):
		actor.draw_card(self.face_up)
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
		x=self.get_x()+c*(self.column_width+self.spacing)+self.spacing
		y=self.get_y()+r*(self.row_height+self.spacing)+self.spacing
		if add_to_stage:
			self.app.stage.add_actor(actor)
		if time != 0:
			go_to(actor,x,y,time)
		else:
			actor.set_position(x,y)
	
	def add_on(self, actor, on_actor, time, add_to_stage=True):
		actor.draw_card(self.face_up)
		x=on_actor.get_x()+30
		y=on_actor.get_y()+30
		if add_to_stage:
			self.app.stage.add_actor(actor)
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
	
	def destroy(self):
		for row in range(self.rows):
			for col in range(self.cols):
				if self.children[row][col] != 0:
					self.children[row][col].destroy()
		Clutter.Actor.destroy(self)
	
	def show_all(self):
		for row in range(self.rows):
			for col in range(self.cols):
				if self.children[row][col] != 0:
					self.children[row][col].show()
		self.show()

#class child of Clutter.CairoTexture that shows a deck, it also contains the list of cards in it
class Deck(Clutter.Actor):
	def __init__(self, app, with_scopa=False, padding=15):
		Clutter.Actor.__init__(self)
		self.settings = Gio.Settings.new(base.SCHEMA_ID)
		self.settings.connect("changed::cards", self.update_cards)
		self.app = app
		self.canvas = Clutter.Canvas()
		self.canvas.connect("draw", self._draw)
		self.set_content(self.canvas)
		self.child_w,self.child_h = base.get_card_size()
		self.set_x_expand(False)
		self.set_y_expand(False)
		self.padding = padding
		self.surface = cairo.ImageSurface.create_from_png(base.percorso_carte+self.settings.get_string('cards')+'/'+base.immagini[1][0])
		self.cards = []
		self.with_scopa = with_scopa
		self.scopa_card = None
		self.scope = 0
		if with_scopa:
			self.canvas.set_size(2*(padding+self.child_w),2*padding+self.child_h+20)
		else:
			self.canvas.set_size(2*padding+self.child_w+20,2*padding+self.child_h+20)
	
	def populate(self):
		for suit in range(4):
			for value in range(1,11):
				self.cards.append(Card(suit, value))
		
	def get_min_width(self):
		if self.with_scopa:
			return 2*(self.padding+self.child_w)
		else:
			return 2*self.padding+self.child_w+20

	def get_min_height(self):
			return 2*self.padding+self.child_h+20
		
	def get_natural_width(self):
		if self.with_scopa:
			return 2*(self.padding+self.child_w)
		else:
			return 2*self.padding+self.child_w+20
	
	def get_natural_height(self):
			return 2*self.padding+self.child_h+20
	
	def draw(self, *data):
		self.canvas.invalidate()
	
	def _draw(self, canvas, cr, width, height):
		self.set_size(width,height)
		cr.set_operator(cairo.OPERATOR_CLEAR)
		cr.paint()
		cr.set_operator(cairo.OPERATOR_OVER)
		if self.with_scopa:
			if self.scopa_card != None:
				surface = cairo.ImageSurface.create_from_png(base.percorso_carte+self.settings.get_string('cards')+'/'+base.immagini[self.scopa_card.suit][self.scopa_card.value])
				cr.set_source_surface(surface,self.padding+self.child_w,self.padding)
				cr.paint()
			if self.scope != 0:
				cr.set_font_size(15)
				xb, yb, w, h, xadvance, yadvance = (cr.text_extents(str(self.scope)))
				w,h=int(w),int(h)
				sur = cairo.ImageSurface(cairo.FORMAT_ARGB32,w+10,h+10)
				tmp = cairo.Context(sur)
				tmp.set_source_rgb(0,0,0)
				tmp.paint()
				tmp.set_source_rgb(1,1,1)
				tmp.set_font_size(15)
				tmp.move_to(5,h+5)
				tmp.show_text(str(self.scope))
				cr.set_source_surface(sur,self.get_width()-w-10-self.padding,self.padding)
				cr.paint()
		c=(len(self.cards)+3)/4
		n=0
		while n<c:
			cr.set_source_surface(self.surface,n+self.padding,n+self.padding)
			cr.paint()
			n=n+1
		return True
	
	def update_cards(self, settings=None, key=None):
		self.surface = cairo.ImageSurface.create_from_png(base.percorso_carte+self.settings.get_string('cards')+'/'+base.immagini[1][0])
		self.child_w,self.child_h = base.get_card_size()
		if self.with_scopa:
			self.canvas.set_size(2*(self.padding+self.child_w),2*self.padding+self.child_h+20)
		else:
			self.canvas.set_size(2*self.padding+self.child_w+20,2*self.padding+self.child_h+20)
		self.draw()

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
		y=self.get_y()
		x=self.get_x()
		if add_to_stage:
			self.app.stage.add_actor(actor)
		if time != 0:
			animation = go_to(actor,x+self.padding,y+self.padding,time)
			animation.connect('completed', base.hide_data, actor)
			animation.connect('completed', self.draw)
		else:
			actor.set_position(x,y)
	
	def add_scopa(self, card=None, scope=None):
		if card != None:
			self.scopa_card = card
			if scope == None:
				self.scope += 1
		if scope != None:
			self.scope += scope
		self.draw()
	
	def reset(self):
		for card in self.cards:
			card.destroy()
		self.cards = []
		self.scope=0
		self.scopa_card = None
		self.draw()

#This class handles the notifications
class NotificationSystem():
	def __init__(self, table):
		self.table = table
		self.mesg = [0,0,0,0,0,0]

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
		text.set_position(self.table.get_stage().get_size()[0]-w-30,10+i*(h+30))
		self.table.get_stage().add_actor(text)
		self.mesg[i] = text
		cr = text.create()
		cr.set_source_surface(sur,0,0)
		cr.paint()
		text.invalidate()
		if time != 0:
			self.table.timeout_add(time, self.delete, i)
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

def show_summary(app, callback, *cols):
	window = Gtk.Dialog()
	window.set_title(_('Game summary'))
	window.set_transient_for(app.mainWindow)
	window.set_position(Gtk.WindowPosition.CENTER_ON_PARENT)
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
