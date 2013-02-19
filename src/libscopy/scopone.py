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

from libscopyUI import widgets
from libscopy import core
from gettext import gettext as _
import random

n_players = [4]

Player=core.Player
Ai=core.Ai

class Partita(core.Partita):
	def __init__(self, table, stage, players, end):
		if len(players) not in n_players:
			raise Exception('Numero di giocatori sbagliato')
		self.mazzo = widgets.Deck()
		self.carte_terra = widgets.Box(2,5)
		self.players = [Player(players[0],widgets.Box(1,10))]
		table.pack(self.mazzo,0,0)
		table.pack(self.carte_terra,1,1)
		table.pack(self.players[0].mano, 1,2)
		self.mazzo.populate()
		self.mazzo.draw()
		self.mazzo.mix()
		if len(players)==4:
			self.players.append(Ai(players[1],widgets.Box(10,1)))
			self.players.append(Ai(players[2],widgets.Box(1,10),self.players[0].carte_prese,self.players[0].scope))
			self.players.append(Ai(players[3],widgets.Box(10,1),self.players[1].carte_prese,self.players[1].scope))
			self.teams = (
				(players[0]+'/'+players[2],self.players[0]),
				(players[1]+'/'+players[3],self.players[1]))
			table.pack(self.players[1].mano, 2,1)
			table.pack(self.players[2].mano, 1,0)
			table.pack(self.players[3].mano, 0,1)
			table.pack(self.players[0].carte_prese, 2,2)
			table.pack(self.players[1].carte_prese, 2,0)
			table.pack(self.players[0].scope, 3,2)
			table.pack(self.players[1].scope, 3,0)
			h=stage.get_height()-2*self.players[0].mano.get_height()-65
			self.players[1].mano.set_max_height(h)
			self.players[3].mano.set_max_height(h)
			w=stage.get_width()-3*self.mazzo.get_width()
			self.players[0].mano.set_max_width(w)
			self.players[2].mano.set_max_width(w)
		table.set_fill(self.carte_terra,False,False)
		for player in self.players:
			table.set_fill(player.mano,False,False)
			table.set_fill(player.carte_prese,False,False)
			table.set_fill(player.scope,False,False)
		self.stage = stage
		self.notifiche = widgets.NotificationSystem(stage)
		self.giocatore = random.randrange(len(players))
		self.punti_vit = 11
		self.player_can_play = False
		self.mano = 0
		self.ultimo_prende = 0
		self.end = end
		
	#distribuisce le carte ai giocatori e a terra se è la prima mano
	def distribuisci_carte(self):
		for player in self.players:
			for n in range(10):
				card=self.mazzo.pop()
				if player.ai:
					card.draw_card(1)
				else:
					card.draw_card()
					card.activate(self.play)
				player.mano.add(card)
		if self.mano == 0:
			if self.giocatore == 0:
				self.notifiche.notify(_("It's your turn"),2000)
			else:
				self.notifiche.notify(_("%s starts"%self.players[self.giocatore].name),2000)