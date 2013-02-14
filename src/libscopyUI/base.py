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

import sys, os

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

#tempo in ms da aspettare dopo che una carta viene giocata
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

#default settings
default = {
			'nome':_('Player'),
			'variante':_('Classic scopa'),
			'speed':'3',
			'cards':'Napoletane',
			'sfondo':'verde',
			}

class Settings():
	def __init__(self):
		self.settings = {}
		self.load()
		self.check()
	
	def __getitem__(self, key):
		return self.settings[key]
	
	def __setitem__(self, key, value):
		self.settings[key] = value

	def load(self):
		d = os.path.expanduser('~')+"/.scopy"
		if not os.path.exists(d):
			os.makedirs(d)
			config = open(os.path.expanduser('~')+"/.scopy/settings.conf", 'w')
			config.close()
			for key in default:
				self[key] = default[key]
			self.save()
		else:
			try:
				f = open(os.path.expanduser('~')+"/.scopy/settings.conf")
				line = f.readline()
				while line != '':
					try:
						pos_uguale = line.index('=')
					except:
						break
					self[line[0:pos_uguale]]=line[pos_uguale+1:-1]
					line = f.readline()
				for key in default:
					if not key in self.settings:
						self[key] = default[key]
				self.save()
			except:
				for key in default:
					self[key] = default[key]
				self.save()
	
	def check(self):
		if self['variante'] not in varianti:
			self['variante'] = default['variante']
		if self['cards'] not in tipi_di_carte:
			self['cards'] = default['cards']
		if self['sfondo'] not in sfondi:
			self['sfondo'] = default['sfondo']

	def save(self):
		config = open(os.path.expanduser('~')+"/.scopy/settings.conf", 'w')
		for key in self.settings:
			config.write(key+'='+self[key]+'\n')
		config.close()

settings=Settings()
