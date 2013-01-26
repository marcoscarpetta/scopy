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

import random
from gi.repository import Clutter,GLib
from libscopyUI import base
import itertools

pali_str = ["denari", "coppe", "bastoni", "spade"]
valori_str = ["", "asso", "2", "3", "4", "5", "6", "7", "donna", "cavallo" ,"re"]
valori_set = [0, 16, 12, 13, 14, 15, 18, 21, 10, 10, 10]

class Player():
	def __init__(self, name, mano):
		if name == '':
			self.name = 'Giocatore'
		else:
			self.name = name
		self.mano = mano
		self.carte_prese = base.Deck()
		self.punti = 0
		self.scope = base.Scope()
		self.ult_scopa = [0,0]
		self.scoperte = 0
		self.ai=False

class Ai(Player):
	def __init__(self, name, mano):
		Player.__init__(self, name, mano)
		self.ai=True

class Partita():
	def __init__(self, grid, players):		
		if len(players) not in (2,4):
			raise Exception('Numero di giocatori sbagliato')
		if len(players)==2:
			self.players = [Player(players[0],base.Box(1,3))]
			self.players.append(Ai(players[1],base.Box(1,3)))
			self.carte_terra = base.Box(2,5)
			self.mazzo = base.Deck()
			grid.pack(self.mazzo, 0,0)
			self.mazzo.populate()
			self.mazzo.draw()
			self.mazzo.mischia()
			grid.pack(self.carte_terra,1,1)
			grid.pack(self.players[0].mano, 1,2)
			grid.pack(self.players[1].mano, 1,0)
			grid.pack(self.players[0].carte_prese, 2,2)
			grid.pack(self.players[1].carte_prese, 2,0)
			grid.pack(self.players[0].scope, 3,2)
			grid.pack(self.players[1].scope, 3,0)
		self.giocatore = random.randrange(len(players))
		self.punti_vit = 11
		self.player_can_play = False
		self.mano = 0
		self.ultimo_prende = 0

	def start(self):
		self.distribuisci_carte()
		GLib.timeout_add(2000,self.prossimo_giocatore)
	
	#distribuisce le carte ai giocatori e a terra se è la prima mano
	def distribuisci_carte(self):
		for player in self.players:
			for n in range(3):
				card=self.mazzo.pop()
				if player.ai:
					card.draw_card(1)
				else:
					card.draw_card()
					card.activate(self.play)
				player.mano.add(card)
		if self.mano == 0:
			for n in range(4):
				card=self.mazzo.pop()
				card.draw_card()
				self.carte_terra.add(card)
	
	#calcola il prossimo giocatore e lo fa giocare
	def prossimo_giocatore(self):
		if self.giocatore+1<len(self.players):
			self.giocatore += 1
		else:
			self.giocatore = 0
		mano_finita = True
		for player in self.players:
			if len(player.mano.get_list())!=0:
				mano_finita = False
				break
		if mano_finita:
			self.mano += 1
			if len(self.carte_terra.get_list())!=0:
				self.distribuisci_carte()
				GLib.timeout_add(2000,self.prossimo_giocatore)
			else:
				self.conta_punti()
		else:
			if self.players[self.giocatore].ai:
				self.gioca_ai()
			else:
				self.player_can_play = True

	#funzione chiamata quando si clicka su una carta del giocatore
	def play(self, card, event, data=None):
		if self.player_can_play:
			prese_possibili = self.prese(card)
			self.gioca_carta(0, card, prese_possibili[0])
	
	#prende le carte da terra e le sposta nelle carte prese dal giocatore
	def presa_da_terra(self, giocatore, carta, carte):
		self.carte_terra.move_to(carta, self.players[giocatore].carte_prese)
		for carta in carte:
			self.carte_terra.move_to(carta, self.players[giocatore].carte_prese)
		GLib.timeout_add(500,self.prossimo_giocatore)

	#gioca la carta indicata del giocatore indicato e prende le carte indicate da terra
	def gioca_carta(self, giocatore, carta, carte):
		if self.players[giocatore].ai:
			carta.draw_card()
		else:
			carta.disconnect_by_func(carta.enter)
			carta.disconnect_by_func(carta.leave)
			self.player_can_play = False
		#se non si prende niente
		if len(carte) == 0:
			self.players[giocatore].mano.move_to(carta, self.carte_terra)
			GLib.timeout_add(2000,self.prossimo_giocatore)
		#se si prende qualcosa
		else:
			self.ult_prende = giocatore
			self.players[giocatore].mano.move_on(carta, carte[0], self.carte_terra)
			n = 0
			#verifica se si fa scopa
			if len(self.mazzo.get_list()) == 0 and len(self.players[0].mano.get_list())==0 and len(self.players[1].mano.get_list())==0:
				pass
			else:
				if len(carte) == len(self.carte_terra.get_list()):
					GLib.timeout_add(2500, self.players[giocatore].scope.add_scopa, carta)
			#prende le carte da terra
			GLib.timeout_add(2000, self.presa_da_terra,giocatore,carta,carte)

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
				#DA RIVEDERE
				'''
				#non 7 a terra
				if len(self.prese(sette)) != 0:
					valore = valore - 1
				#presa dopo
				for carta in carte_mano:
					if carta != carte_mano[ide_carta]:
						if len(self.prese(carta)) != 0:
							valore = valore + 1
				'''
				#scopa avversario
				valore_terra = 0
				for carta in carte_terra:
					valore_terra += carta.value
				valore_terra += carta_da_giocare.value
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
				#scopa avversario
				for carta in carte_terra:
					if not carta in giocata[1]:
						valore_terra += carta.value
				if giocata[1] == []:
					valore_terra += giocata[0].value
				if valore_terra <= 10:
					valore -= 6
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
	
	#ritorna tutte le combinazioni di almeno 2 carte
	def combinazioni(self, lista):
		combinazioni = []
		for i in range(2,len(lista)+1):
			lista_combinazioni = itertools.combinations(lista, i)
			for combinazione in lista_combinazioni:
				combinazioni.append(combinazione)
		return combinazioni

	#ritorna tutte le prese effetuabili con la carta
	def prese(self, card, carte=0):
		if carte == 0:
			carte = self.carte_terra.get_list()
		prese = []
		for carta in carte:
			if card.value == carta.value:
				prese.append([carta])

		if len(prese) == 0:
			lista_combinazioni = self.combinazioni(carte)
			for combinazione in lista_combinazioni:
				somma = 0
				for carta in combinazione:
					somma = somma + carta.value
				if somma == card.value:
					prese.append(combinazione)
		if prese == []:
			return [[]]
		else:			
			return prese

	#conta i punti alla fine della partita
	def conta_punti(self):
		#trasferisce le carte rimaste a terra a l'ultimo giocatore a prendere
		for carta in self.carte_terra.carte:
			self.giocatore[self.ult_prende].carte_prese.carte.append(carta)
		#conta i punti
		ritorno = {}
		#assegna le carte a lunga
		parziale = [0,0]
		if len(self.giocatore[0].carte_prese.carte) > len(self.giocatore[1].carte_prese.carte):
			self.giocatore[0].punti = self.giocatore[0].punti + 1
			parziale[0] = parziale[0] + 1
		elif len(self.giocatore[1].carte_prese.carte) > len(self.giocatore[0].carte_prese.carte):
			self.giocatore[1].punti = self.giocatore[1].punti + 1
			parziale[1] = parziale[1] + 1
		ritorno['Carte'] = [len(self.giocatore[0].carte_prese.carte), len(self.giocatore[1].carte_prese.carte)]
		#assegna la settanta
		valori_pali = [[0,0,0,0],[0,0,0,0]]
		n = 0
		while n < 2:
			i = 0
			while i < 4:
				for carta in self.giocatore[n].carte_prese.carte:
					if carta.palo == i:
						if valori_set[carta.valore] > valori_pali[n][i]:
							valori_pali[n][i] = valori_set[carta.valore]
				i = i+1
			n = n+1
		somma = [0,0]
		somma[0] = valori_pali[0][0]+valori_pali[0][1]+valori_pali[0][2]+valori_pali[0][3]
		somma[1] = valori_pali[1][0]+valori_pali[1][1]+valori_pali[1][2]+valori_pali[1][3]
		if somma[0] > somma[1]:
			self.giocatore[0].punti = self.giocatore[0].punti + 1
			parziale[0] = parziale[0] + 1
		elif somma[1] > somma[0]:
			self.giocatore[1].punti = self.giocatore[1].punti + 1
			parziale[1] = parziale[1] + 1
		ritorno['Primiera'] = somma
		#assegna il 7 bello
		for carta in self.giocatore[0].carte_prese.carte:
			if carta.palo == 0 and carta.valore == 7:
				self.giocatore[0].punti = self.giocatore[0].punti + 1
				parziale[0] = parziale[0] + 1
				ritorno['Sette Bello'] = [1,0]
		for carta in self.giocatore[1].carte_prese.carte:
			if carta.palo == 0 and carta.valore == 7:
				self.giocatore[1].punti = self.giocatore[1].punti + 1
				parziale[1] = parziale[1] + 1
				ritorno['Sette Bello'] = [0,1]
		#assegna i denari
		denari = [0,0]
		n = 0
		while n < 2:
			for carta in self.giocatore[n].carte_prese.carte:
				if carta.palo == 0 :
					denari[n] = denari[n] + 1
			n = n+1
		if denari[0] > denari[1]:
			self.giocatore[0].punti = self.giocatore[0].punti + 1
			parziale[0] = parziale[0] + 1
		elif denari[1] > denari[0]:
			self.giocatore[1].punti = self.giocatore[1].punti + 1
			parziale[1] = parziale[1] + 1
		ritorno['Denari'] = denari
		#assegna le scope
		self.giocatore[0].punti = self.giocatore[0].punti + self.giocatore[0].scope
		parziale[0] = parziale[0] + self.giocatore[0].scope
		self.giocatore[1].punti = self.giocatore[1].punti + self.giocatore[1].scope
		parziale[1] = parziale[1] + self.giocatore[1].scope
		ritorno['Scope'] = [self.giocatore[0].scope, self.giocatore[1].scope]
		ritorno['Parziale'] = parziale
		return ritorno

	#azzera la partita quando si finisce il mazzo
	def azzera(self):
		self.mazzo = mazzo(40)
		self.mazzo.mischia()
		self.carte_terra = mazzo()
		for giocatore in self.giocatore:
			giocatore.mano = mazzo()
			giocatore.carte_prese = mazzo()
			giocatore.scope = 0
			giocatore.ult_scopa = [0, 0]
		self.ide = altro(self.ide)
		self.mano = 0