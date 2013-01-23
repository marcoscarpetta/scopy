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
		#creazione varie finestre
		self.crea_riepilogo()
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

	### CREAZIONE FINESTRE ####
	def crea_riepilogo(self):
		self.rie = Gtk.Dialog()
		self.rie.set_title(_('Game summary'))
		self.rie.set_transient_for(self.window)
		self.rie.set_position(Gtk.WindowPosition.CENTER_ON_PARENT)
		self.rie.set_border_width(10)
		self.rie.add_button(_('OK'), 0)
		self.rie.set_default_response(0)
		self.rie.connect('response', self.end_riepilogo)
		hbox = self.rie.get_content_area()
		box=Gtk.HBox()
		hbox.pack_start(box,True,True,5)
		box.set_spacing(5)
		self.rie_labels=[Gtk.Label(),Gtk.Label(),Gtk.Label()]
		box.pack_start(self.rie_labels[0],True,True,5)
		box.pack_start(self.rie_labels[1],True,True,5)
		box.pack_start(self.rie_labels[2],True,True,5)
	### FUNZIONI CHE MOSRTANO LE FINESTRE ALLE RISPETTIVE PRESSIONI DELLE VOCI DEI MENU ####
	def show_riepilogo(self, colonne=None):
		for obj in self.carte.carte:
			obj.object.destroy()
		self.boxes['prese_c'].clean()
		self.boxes['prese_g'].clean()
		self.boxes['scope_c'].clean()
		self.boxes['scope_g'].clean()
		self.boxes['terra'].clean()
		self.carte = Carte()
		if colonne == None:
			punti = self.partita.conta_punti()
			colonne = ['\n',self.partita.giocatore[0].nome+'\n','Computer'+'\n']
			for voce in punti:
				if voce != 'Parziale':
					colonne[0] = colonne[0] + voce + '\n'
					colonne[1] = colonne[1] + str(punti[voce][0]) + '\n'
					colonne[2] = colonne[2] + str(punti[voce][1]) + '\n'
			colonne[0] = colonne[0] + 'Parziale' + '\n'
			colonne[1] = colonne[1] + str(punti['Parziale'][0]) + '\n'
			colonne[2] = colonne[2] + str(punti['Parziale'][1]) + '\n'
			colonne[0] = colonne[0] + 'Punti'
			colonne[1] = colonne[1] + str(self.partita.giocatore[0].punti)
			colonne[2] = colonne[2] + str(self.partita.giocatore[1].punti)
		self.rie_labels[0].set_text(colonne[0])
		self.rie_labels[1].set_text(colonne[1])
		self.rie_labels[2].set_text(colonne[2])
		self.rie.show_all()
	#nasconde la finestra di riepilogo e procede con il gioco
	def end_riepilogo(self, widget=None, data=None):
		self.hide(self.rie)
		if self.partita.giocatore[0].punti >= self.partita.punti_vit or self.partita.giocatore[1].punti >= self.partita.punti_vit and self.partita.giocatore[0].punti != self.partita.giocatore[1].punti:
			if self.partita.giocatore[0].punti > self.partita.giocatore[1].punti:
				self.comunica(_('You won!'), 2000)
			else:
				self.comunica(_('I won!'), 2000)
			GLib.timeout_add(2000, Start.main, None, self)
		else:
			self.partita.azzera()
			self.dichiara(self.partita.dai_carte())
			self.sposta_carte()

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
		if self.opzioni['variante'] == None:
			from libscopy import classica
			self.partita = classica.partita(self.opzioni['nome'],nc)
		if self.opzioni['variante'] == _('Classic scopa'):
			from libscopy import core
			self.partita = core.Partita(self.grid, (self.opzioni['nome'],nc))
		if self.opzioni['variante'] == _('Cirulla'):
			from libscopy import cirulla
			self.partita = cirulla.partita(self.opzioni['nome'],nc)
		if self.opzioni['variante'] == _('Cucita'):
			from libscopy import cucita
			self.partita = cucita.partita(self.opzioni['nome'],nc)
		if self.opzioni['variante'] == _('Re Bello'):
			from libscopy import re_bello
			self.partita = re_bello.partita(self.opzioni['nome'],nc)

	#dichiara le combinazioni di carte, es. nella Cirulla
	def dichiara(self, dichiarazione):
		for n in range(2):
			if dichiarazione != None:
				testo=''
				if 0 in dichiarazione[n]:
					testo = _('Sum lower then 9')
					if 1 in dichiarazione[n]:
						testo = testo + _(' and 3 egual cards')
				elif 1 in dichiarazione[n]:
						testo = testo + _('3 egual cards')
				if testo != '':
					testo = self.partita.giocatore[n].nome+': '+testo
					self.comunica(testo, 5000)

	#funzione che mostra l'interfaccia per scegliere una presa
	def scelta_presa(self, obj, prese_possibili):
		i=self.stage.get_n_children()
		n=0
		while n<i:
			if self.stage.get_nth_child(n) != self.back_img:
				self.stage.get_nth_child(n).hide()
			n=n+1
		index = self.comunica(_('What do you take?'),0)
		w, h = self.carte.carte[0].object.get_width(), self.carte.carte[0].object.get_height()
		box=[]
		n=0
		while n<len(prese_possibili):			
			if n != 0:
				box.append(Box(self.stage,1,len(prese_possibili[n]),0,box[n-1].get_height()+box[n-1].get_y(),20,10,w,h))
			else:
				box.append(Box(self.stage,1,len(prese_possibili[n]),0,0,20,10,w,h))
			i=0
			while i < len(prese_possibili[n]):
				carta = self.partita.carte_terra[prese_possibili[n][i]]
				actor = Clutter.Texture.new_from_file(percorso_carte+self.opzioni['carte']+'/'+immagini[carta.palo][carta.valore])
				box[n].add(actor,0)
				actor.set_reactive(True)
				actor.connect('button-press-event',self.scelta_fatta,box,obj,n,index)
				i=i+1
			n=n+1
	#funzione eseguita quando si è scelta una presa
	def scelta_fatta(self, actor,data,oggetti,obj,n,index):
		self.delete(index)
		for box in oggetti:
			box.destroy()
		i=self.stage.get_n_children()
		g=0
		while g<i:
			self.stage.get_nth_child(g).show()
			g=g+1
		self.set_giocatore_can_play()
		self.gioca_giocatore(obj,data, n)

	#scrive 'messaggio' al centro dello schermo per 'time' ms
	def comunica(self, messaggio, time):
		sur = cairo.ImageSurface(cairo.FORMAT_ARGB32,500,500)
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
		text.set_position(self.window.get_size()[0]-w-30,10+i*(h+30))
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
main_win = main_win()
Start.main(None, main_win)
Gtk.main()
