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

ai_values = (
	### nessuna presa
	lambda mem: 1, #2 carte uguali
	lambda mem: 1, #non denari
	lambda mem: 1,	#non 7
	lambda mem: 1, #carta piu' bassa
	lambda mem: -1, #non 7 a terra (turno successivo)
	lambda mem: 1,	#presa dopo
	lambda mem: -10,	#carte avversario scoperte, scopa dopo (a)
	lambda mem: -5,	#carte avversario scoperte, presa dopo, 0 se (a)==1
	lambda mem: -6, #possibile scopa avversario, 0 se (a)==1
	### almeno una presa
	lambda mem: 20, #scopa
	lambda mem: -6,	#carte avversario scoperte, scopa dopo (b)
	lambda mem: -1,	#carte avversario scoperte, presa dopo, 0 se (b)==1
	lambda mem: -6, #probabile scopa avversario, 0 se (b)==1
	### se non si prende niente
	lambda mem: 1, #non denaro
	lambda mem: 1, #non 7
	lambda mem: 1, #carta piu' bassa
	### se si prende qualcosa
	lambda mem: 1, #ogni carta presa
	lambda mem: 3, #ogni denaro
	lambda mem: (mem['7'] > 2)*4, #ogni sette
	lambda mem: 20, #sette bello
	lambda mem: 6, #ogni sei
	lambda mem: 1, #ogni asso
	)

class Match(core.Match):
	def __init__(self, app, players):
		core.Match.__init__(self, app, players)
		self.punti_vit = 51

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
			valore_uguali = 0
			sette = None
			for n in range(3):
				card = self.mazzo.pop()
				carte.append(card)
				somma += card.value
				if card.value in prev:
					uguali += 1
					valore_uguali = card.value
				prev.append(card.value)
				if card.value == 7 and card.suit == 0:
					sette=card
			if somma <= 9:
				player.carte_prese.add_scopa(None,3)
				self.notifiche.notify(_("The sum of %s's cards is minor then 10"%player.name),5000)
				player.scoperte = 1
			elif sette:
				if somma-6 <= 9:
					player.carte_prese.add_scopa(None,3)
					self.notifiche.notify(_("The sum of %s's cards is minor then 10"%player.name),5000)
					player.scoperte = 1
					sette.new_value=1
			if uguali == 2 and sette and valore_uguali != 7:
				player.carte_prese.add_scopa(None,10)
				self.notifiche.notify(_("%s has 3 equals cards"%player.name),5000)
				player.scoperte = 1
				sette.new_value = valore_uguali
			if uguali == 3:
				player.carte_prese.add_scopa(None,10)
				self.notifiche.notify(_("%s has 3 equals cards"%player.name),5000)
				player.scoperte = 1
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
		else:
			migliore = [carte_mano[0],[],-1000]
			for giocata in giocate:
				par = []
				flag = no_prese
				### no_prese = 1
				#2 carte uguali
				n = 0
				for carta in carte_mano:
					if carta.value == giocata[0].value:
						n = n+1
				par.append((n>=2)*flag)
			
				#non denari
				par.append((giocata[0].suit != 0)*flag)
			
				#non 7
				par.append((giocata[0].value != 7)*flag)
			
				#carta piu' bassa
				n = 0
				for carta in carte_mano:
					if carta.value >= giocata[0].value:
						n = n + 1
				par.append((n == len(carte_mano))*flag)
			
				#non 7 a terra
				n=0
				if len(self.prese(widgets.Card(0,7),carte_terra+[giocata[0]])) != 0:
					n=1
				par.append(n*flag)
			
				#presa dopo
				presa_dopo = 0
				for carta in carte_mano:
					if carta != giocata[0]:
						if len(self.prese(carta,carte_terra+[giocata[0]])) != 0:
							presa_dopo += 1
				par.append(presa_dopo*flag)
				
				#carte avversario conosciute
				scopa_avversario = 0
				presa_avversario = 0
				if self.players[self.next()].scoperte:
					for carta in self.players[self.next()].mano.get_list():
						for presa in self.prese(carta, carte_terra+[giocata[0]]):
							if len(presa) == len(carte_terra)+1:
								scopa_avversario = 1
							presa_avversario = 1
				par.append(scopa_avversario*flag)
				par.append((not scopa_avversario)*presa_avversario*flag)
				
				#scopa avversario
				valore_terra = giocata[0].value
				for carta in carte_terra:
					valore_terra += carta.value
				par.append((not scopa_avversario)*(valore_terra <= 10)*flag)

				### no_prese=0
				flag = not no_prese
				#scopa
				par.append((len(giocata[1]) == len(carte_terra))*flag)
			
				#
				valore_terra = 0
 				carte_da_lasciare=[]
				for carta in carte_terra:
					if not carta in giocata[1]:
						valore_terra += carta.value
						carte_da_lasciare.append(carta)
				if giocata[1] == []:
					valore_terra += giocata[0].value
					carte_da_lasciare.append(giocata[0])
				
				#carte avversario conosciute
				scopa_avversario = 0
				presa_avversario = 0
				if self.players[self.next()].scoperte:
					for carta in self.players[self.next()].mano.get_list():
						for presa in self.prese(carta, carte_da_lasciare):
							if len(presa) == len(carte_da_lasciare):
								scopa_avversario = 1
							presa_avversario = 1
				par.append(scopa_avversario*flag)
				par.append((not scopa_avversario)*presa_avversario*flag)
				
				#probabile scopa avversario
				par.append((not scopa_avversario)*(valore_terra <= 10)*flag)
			
				### se non si prende niente
				flag = (not no_prese)*(len(giocata[1]) == 0)
			
				#non denaro
				par.append((giocata[0].suit != 0)*flag)
			
				#non 7
				par.append((giocata[0].value != 7)*flag)
			
				#carta piu' bassa
				for carta in carte_mano:
					if carta.value > giocata[0].value:
						n = n + 1
				par.append((n == len(carte_mano))*flag)
			
				### se si prende qualcosa
				flag = (not no_prese)*(len(giocata[1]) != 0)
				carte_da_prendere=list(giocata[1])
				carte_da_prendere.append(giocata[0])
			
				#numero carte prese
				par.append(len(carte_da_prendere)*flag)
			
				tmp = [0,0,0,0,0]
				for carta in carte_da_prendere:
					#se denaro
					if carta.suit == 0:
						tmp[0] += 1
					#se sette
					if carta.value == 7:
						tmp[1] += 1
						#se sette bello
						if carta.suit == 0:
							tmp[2] += 1
					#se sei
					if carta.value == 6:
						tmp[3] += 1
					#se asso
					if carta.value == 1:
						tmp[4] += 1
				for v in tmp:
					par.append(v*flag)
				
				value = self.players[self.giocatore].value(par, ai_values)
				if value > migliore[2]:
					migliore[0], migliore[1], migliore[2] = giocata[0], giocata[1], value
				
		self.gioca_carta(self.giocatore,migliore[0],migliore[1])

	#ritorna tutte le prese effetuabili con la carta
	def prese(self, card, carte=None):
		try:
 			valore = card.new_value
 		except:
 			valore = card.value
		if carte == None:
			carte = self.carte_terra.get_list()
		prese = []
		for carta in carte:
			if valore == carta.value:
				prese.append([carta])
			if valore + carta.value == 15:
				prese.append([carta])

		lista_combinazioni = self.combinazioni(carte)
		for combinazione in lista_combinazioni:
			somma = 0
			for carta in combinazione:
				somma = somma + carta.value
			if somma == valore:
				prese.append(combinazione)
			if valore+somma==15:
				prese.append(combinazione)
 		if valore == 1:
			asso=0
 			for carta in carte:
				if carta.value==1:
					asso=1
			if not asso:
				prese.append(carte)
		if prese == []:
			return [[]]
		else:			
			return prese

	#conta i punti alla fine della partita
	def conta_punti(self):
		#trasferisce le carte rimaste a terra a l'ultimo giocatore a prendere
		for carta in self.carte_terra.get_list():
			self.carte_terra.move_to(carta, self.players[self.ult_prende].carte_prese)
		#conta i punti
		legenda = '\n'+_('Cards')+'\n'+\
			_('Primiera')+'\n'+\
			_('Seven of Coins')+'\n'+\
			_('Coins')+'\n'+\
			_('Scope')+'\n'+\
			_('Partial')+'\n'+\
			_('Total')
		punti=[]
		n=0
		while n<len(self.teams):
			carte_prese = self.teams[n][1].carte_prese.get_list()
			punti.append([])
			
			punti[n].append(len(carte_prese))

			valori_pali = [0,0,0,0]
			i = 0
			while i < 4:
				for carta in carte_prese:
					if carta.suit == i:
						if core.valori_set[carta.value] > valori_pali[i]:
							valori_pali[i] = core.valori_set[carta.value]
				i += 1
			punti[n].append(sum(valori_pali))
			
			denari = []
			punti[n].append(0)
			punti[n].append(0)
			for carta in carte_prese:
				if carta.suit == 0:
					punti[n][3] += 1
					denari.append(carta.suit)
					if carta.value == 7:
						punti[n][2] = 1
			a=1
			while a in denari: a+=1
			if a>2: self.teams[n][1].carte_prese.scope += a
			a=10
			while a in denari: a-=1
			if a<9: self.teams[n][1].carte_prese.scope += 11-a
			n += 1
		
		n=0
		while n < len(self.teams):
			self.teams[n][1].punti += self.teams[n][1].carte_prese.scope
			punti[n].append(self.teams[n][1].carte_prese.scope)
			punti[n].append(self.teams[n][1].carte_prese.scope)
			n += 1

		i=0
		while i<4:
			massimo = 0
			pari = 0
			n=1
			while n<len(self.teams):
				if punti[n][i] >= punti[massimo][i]:
					pari = 0
					if punti[n][i] == punti[massimo][i]:
						pari = 1
					massimo = n	
				n += 1
			if pari == 0:
				self.teams[massimo][1].punti += 1
				punti[massimo][5] += 1
			i += 1
		
		colonne = []
		n=0
		while n<len(self.teams):
			colonne.append(self.teams[n][0]+'\n')
			for punto in punti[n]:
				colonne[n] += str(punto)+'\n'
			colonne[n] += str(self.teams[n][1].punti)
			n += 1

		widgets.show_summary(self.app, self.azzera, legenda, *colonne)
