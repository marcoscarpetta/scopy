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
from libscopyUI import widgets
from gettext import gettext as _
import random

n_players = (2,4)

class Match(core.Match):
	def __init__(self, app, players):
		core.Match.__init__(self, app, players)
		self.punti_vit = 21

	#distribuisce le carte ai giocatori e a terra se è la prima mano
	def distribuisci_carte(self):
		situazione = ''
		for team in self.teams:
			situazione += team[0]+': '+str(team[1].punti)+'       '
		self.app.update_status_bar(situazione)
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
	
	#valuta la migliore presa che il computer puo' fare
	def gioca_ai(self):
		carte_mano = self.players[self.giocatore].mano.get_list()
		carte_terra = self.carte_terra.get_list()
		giocate = []
		no_prese = 1
		n = 0
		i = 0
		for carta in carte_mano:
			prese_possibili = self.prese(carta)
			if prese_possibili != [[]]:
				no_prese = 0
			for presa in prese_possibili:
				giocate.append([carta, presa])

		#se solo 1 giocata possibile
		if len(giocate) == 1:
			migliore = giocate[0]
		#se non si puo' prendere
		elif no_prese == 1:
			migliore = [carte_mano[0],[],-20]
			for carta_da_giocare in carte_mano:
				valore = 0
				n = 0
				#2 carte uguali
				for carta in carte_mano:
					if carta.value == carta_da_giocare.value:
						n = n+1
				if n >= 2:
					valore = valore+1
				#non denari
				if carta_da_giocare.suit != 0:
					valore = valore + 1
				#non 7
				if carta_da_giocare.value != 7:
					valore = valore + 1
				n = 0
				#carta piu' bassa
				for carta in carte_mano:
					if carta.value >= carta_da_giocare.value:
						n = n + 1
				if n == len(carte_mano):
					valore = valore + 1
				#non 7 a terra
				if len(self.prese(widgets.Card(self.app,0,7),carte_terra+[carta_da_giocare])) != 0:
					valore = valore - 1
				#presa dopo
				for carta in carte_mano:
					if carta != carta_da_giocare:
						if len(self.prese(carta,carte_terra+[carta_da_giocare])) != 0:
							valore = valore + 1
				#carte avversario conosciute
				if self.players[self.next()].scoperte:
					for carta in self.players[self.next()].mano.get_list():
						for presa in self.prese(carta, carte_terra+[carta_da_giocare]):
							if len(presa) == len(carte_terra)+1:
								valore -= 10
							valore -= 5
				#scopa avversario
				if not self.players[self.next()].scoperte:
					valore_terra = carta_da_giocare.value
					for carta in carte_terra:
						valore_terra += carta.value
					if valore_terra <= 10:
						valore -= 6

				if valore > migliore[2]:
					migliore[0], migliore[2] = carta_da_giocare, valore
		else:
			migliore = [carte_mano[0],[],-20]
			for giocata in giocate:
				valore = 0
				#scopa
				if len(giocata[1]) == len(carte_terra):
					valore = valore + 20
				valore_terra = 0
 				carte_da_lasciare=[]
				#scopa avversario
				for carta in carte_terra:
					if not carta in giocata[1]:
						valore_terra += carta.value
						carte_da_lasciare.append(carta)
				if not self.players[self.next()].scoperte:
					if giocata[1] == []:
						valore_terra += giocata[0].value
					if valore_terra <= 10:
						valore -= 6
				#carte avversario conosciute
				if self.players[self.next()].scoperte:
					for carta in self.players[self.next()].mano.get_list():
						for presa in self.prese(carta, carte_da_lasciare):
							if len(presa) == len(carte_da_lasciare):
								valore -= 6
							valore -= 1
				#se non si prende niente
				if giocata[1] == []:
					#non denaro
					if giocata[0].suit != 0:
						valore += 1
					#non 7
					if giocata[0].value != 7:
						valore += 1
					n = 0
					#carta piu' bassa
					for carta in carte_mano:
						if carta.value > giocata[0].value:
							n = n + 1
					if n == len(carte_mano):
						valore += 1
				#se si prende qualcosa
				else:
					carte_da_prendere=[]
					carte_da_prendere.append(giocata[0])
					for carta in giocata[1]:
						carte_da_prendere.append(carta)	
					valore += len(carte_da_prendere)
					for carta in carte_da_prendere:
						#se denaro
						if carta.suit == 0:
							valore += 3
						#se sette
						if carta.value == 7:
							valore += 4
							#se sette bello
							if carta.suit == 0:
								valore += 20
						#se sei
						if carta.value == 6:
							valore += 2
						#se asso
						if carta.value == 1:
							valore += 1
				if valore > migliore[2]:
					migliore[0], migliore[1], migliore[2] = giocata[0], giocata[1], valore
		self.gioca_carta(self.giocatore,migliore[0],migliore[1])	
