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

from libscopy import core
from gettext import gettext as _
import random

n_players = (2,3,4)

class Partita(core.Partita):
	def __init__(self, grid, stage, players, end):
		core.Partita.__init__(self, grid, stage, players, end)
		self.punti_vit = 21

	#distribuisce le carte ai giocatori e a terra se è la prima mano
	def distribuisci_carte(self):
		for player in self.players:
			carte = []
			player.scoperte = 0
			somma = 0
			prev = []
			uguali = 1
			for n in range(3):
				card = self.mazzo.pop()
				carte.append(card)
				somma += card.value
				if card.value in prev:
					uguali += 1
				prev.append(card.value)
			if somma <= 9:
				player.scope.add_scopa(None,2)
				self.notifiche.notify(_("The sum of %s's cards is minor then 10"%player.name),5000)
				player.scoperte = 1
			if uguali == 2:
				player.scope.add_scopa(None,3)
				self.notifiche.notify(_("%s has 2 equals cards"%player.name),5000)
				player.scoperte = 1
			if uguali == 3:
				player.scope.add_scopa(None,7)
				self.notifiche.notify(_("%s has 3 equals cards"%player.name),5000)
				player.scoperte = 1
			player.scope.draw()
			for card in carte:
				if player.ai:
					card.draw_card(not player.scoperte)
				else:
					card.draw_card()
					card.activate(self.play)
				player.mano.add(card)
			
		if self.mano == 0:
			for n in range(4):
				card=self.mazzo.pop()
				card.draw_card()
				self.carte_terra.add(card)
			if self.giocatore == 0:
				self.notifiche.notify(_("It's your turn"),2000)
			else:
				self.notifiche.notify(_("%s starts"%self.players[self.giocatore].name),2000)