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

import sys, os
import cairo
import pickle
from gi.repository import Gio

APP_VERSION = '1.1.1'
APP_NAME = 'scopy'
SCHEMA_ID = 'apps.scopy'

settings = Gio.Settings.new(SCHEMA_ID)

#setting up gettext
import gettext
from gettext import gettext as _
gettext.bindtextdomain('scopy', '/usr/share/locale')
gettext.textdomain('scopy')

#recupero percorsi dove si trovano le immagini
percorso = sys.path[0][0:-4]
percorso_tap = percorso+'/data/images/tappeti/'
percorso_carte = percorso+'/data/images/carte/'
percorso_doc = percorso+'/doc/'

#destroys the given widget
def destroy(widget, response):
	widget.destroy()

def hide_data(event, data):
	data.hide()

#hides the given widget
def hide(widget, response):
	widget.hide()
	return True

#nomi dei file delle immagini delle carte
immagini = [
	["0.png", "1d.png", "2d.png", "3d.png", "4d.png", "5d.png", "6d.png", "7d.png", "8d.png", "9d.png", "10d.png"],
	["bg.png", "1c.png", "2c.png", "3c.png", "4c.png", "5c.png", "6c.png", "7c.png", "8c.png", "9c.png", "10c.png"],
	["mazzo.png", "1b.png", "2b.png", "3b.png", "4b.png", "5b.png", "6b.png", "7b.png", "8b.png", "9b.png", "10b.png"],
	["0.png", "1s.png", "2s.png", "3s.png", "4s.png", "5s.png", "6s.png", "7s.png", "8s.png", "9s.png", "10s.png"]
]

variants = [_('Classic scopa'), _('Cirulla'), _('Cucita'), _('Re Bello'),_('Scopone')]

def import_variant(variant):
	if variant == _('Classic scopa'):
		from libscopy import core as variant_module
	elif variant == _('Cirulla'):
		from libscopy import cirulla as variant_module
	elif variant == _('Cucita'):
		from libscopy import cucita as variant_module
	elif variant == _('Beautiful King'):
		from libscopy import re_bello as variant_module
	elif variant == _('Scopone'):
		from libscopy import scopone as variant_module
	else:
		from libscopy import core as variant_module
	return variant_module

def get_number_of_players(variant_name):
	variant = import_variant(variant_name)
	return variant.n_players

#tempo in ms da aspettare dopo che una carta viene giocata
times=[1,2000,1000,0]

#caricamento tipi di carte
cards_types = []
for cartella in os.listdir(percorso_carte):
	if cartella[0] != '.':
		cards_types.append(cartella)
cards_types.sort()

def get_card_size():
	card=cairo.ImageSurface.create_from_png(percorso_carte+settings.get_string('cards')+'/'+immagini[0][1])
	return card.get_width(), card.get_height()

def create_match(app):
	players=[settings.get_string('player-name')]
	n_players=int(settings.get_int('players'))
	for p in range(n_players-1):
		players.append(_('CPU')+' '+str(p+1))
	variant = import_variant(settings.get_string('variant'))
	return variant.Match(app, players)

def get_pause():
	return times[settings.get_int('speed')]
