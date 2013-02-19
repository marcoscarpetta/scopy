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

import random
from gi.repository import Clutter,GLib
from libscopyUI import base,widgets
import itertools
from gettext import gettext as _

pali_str = ["denari", "coppe", "bastoni", "spade"]
valori_str = ["", "asso", "2", "3", "4", "5", "6", "7", "donna", "cavallo" ,"re"]
valori_set = [0, 16, 12, 13, 14, 15, 18, 21, 10, 10, 10]
n_players = (2,3,4)

class Player():
	def __init__(self, name, mano, carte_prese=None, scope=None):
		if name == '':
			self.name = 'Giocatore'
		else:
			self.name = name
		self.mano = mano
		if carte_prese:
			self.carte_prese=carte_prese
		else:
			self.carte_prese = widgets.Deck()
		if scope:
			self.scope=scope
		else:
			self.scope = widgets.Scope()
		self.punti = 0
		self.scoperte = 0
		self.ai=False

class Ai(Player):
	def __init__(self, name, mano, carte_prese=None, scope=None):
		Player.__init__(self, name, mano, carte_prese, scope)
		self.ai=True

class Partita():
	def __init__(self, table, stage, players, end):		
		if len(players) not in n_players:
			raise Exception('Numero di giocatori sbagliato')
		self.mazzo = widgets.Deck()
		self.carte_terra = widgets.Box(2,5)
		self.players = [Player(players[0],widgets.Box(1,3))]
		table.pack(self.mazzo,0,0)
		table.pack(self.carte_terra,1,1)
		table.pack(self.players[0].mano, 1,2)
		self.mazzo.populate()
		self.mazzo.draw()
		self.mazzo.mix()
		if len(players)==2:
			self.players.append(Ai(players[1],widgets.Box(1,3)))
			self.teams = (
				(self.players[0].name,self.players[0]),
				(self.players[1].name,self.players[1]))
			table.pack(self.players[1].mano, 1,0)
			table.pack(self.players[0].carte_prese, 2,2)
			table.pack(self.players[1].carte_prese, 2,0)
			table.pack(self.players[0].scope, 3,2)
			table.pack(self.players[1].scope, 3,0)
		if len(players)==4:
			self.players.append(Ai(players[1],widgets.Box(3,1)))
			self.players.append(Ai(players[2],widgets.Box(1,3),self.players[0].carte_prese,self.players[0].scope))
			self.players.append(Ai(players[3],widgets.Box(3,1),self.players[1].carte_prese,self.players[1].scope))
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
			if self.giocatore == 0:
				self.notifiche.notify(_("It's your turn"),2000)
			else:
				self.notifiche.notify(_("%s starts"%self.players[self.giocatore].name),2000)
	
	#calcola il prossimo giocatore e lo fa giocare
	def prossimo_giocatore(self):
		mano_finita = True
		for player in self.players:
			if len(player.mano.get_list())!=0:
				mano_finita = False
				break
		if mano_finita:
			self.mano += 1
			if len(self.mazzo.get_list())!=0:
				self.distribuisci_carte()
				GLib.timeout_add(2000,self.prossimo_giocatore)
			else:
				self.conta_punti()
		else:
			if self.players[self.giocatore].ai:
				self.gioca_ai()
			else:
				self.player_can_play = True
			if self.giocatore+1<len(self.players):
				self.giocatore += 1
			else:
				self.giocatore = 0

	#funzione chiamata quando si clicka su una carta del giocatore
	def play(self, card, event, data=None):
		if self.player_can_play:
			prese_possibili = self.prese(card)
			if len(prese_possibili) == 1:
				self.gioca_carta(0, card, prese_possibili[0])
			else:
				self.scelta_presa(card, prese_possibili)
	
	#funzione che mostra l'interfaccia per scegliere una presa
	def scelta_presa(self, carta, prese_possibili):
		self.mazzo.hide()
		self.carte_terra.hide_all()
		for player in self.players:
			player.mano.hide_all()
			player.carte_prese.hide()
			player.scope.hide()
		index = self.notifiche.notify(_('What do you take?'),0)
		boxes=[]
		n=0
		while n<len(prese_possibili):			
			box = widgets.Box(1,len(prese_possibili[n]))
			box.set_position(10,n*(box.get_height()+10))
			self.stage.add_actor(box)
			boxes.append(box)
			i=0
			while i < len(prese_possibili[n]):
				card = widgets.Card(prese_possibili[n][i].suit,prese_possibili[n][i].value)
				card.set_reactive(True)
				card.connect('button-press-event',self.scelta_fatta,boxes,carta,prese_possibili[n],index)
				card.draw_card()
				box.add(card,0)
				i=i+1
			n=n+1

	#funzione eseguita quando si è scelta una presa
	def scelta_fatta(self,actor,event,oggetti,carta,presa,index):
		self.notifiche.delete(index)
		for box in oggetti:
			box.destroy_all()
		self.mazzo.show()
		self.carte_terra.show_all()
		for player in self.players:
			player.mano.show_all()
			player.carte_prese.show()
			player.scope.show()
		self.gioca_carta(0,carta,presa)
	
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
			if self.giocatore+1 < len(self.players):
				GLib.timeout_add(2000,self.prossimo_giocatore)
			else:
				GLib.timeout_add(500,self.prossimo_giocatore)
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
				#non 7 a terra
				if len(self.prese(widgets.Card(0,7),carte_terra+[carta_da_giocare])) != 0:
					valore = valore - 1
				#presa dopo
				for carta in carte_mano:
					if carta != carta_da_giocare:
						if len(self.prese(carta,carte_terra+[carta_da_giocare])) != 0:
							valore = valore + 1
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
	def prese(self, card, carte=None):
		if carte == None:
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
						if valori_set[carta.value] > valori_pali[i]:
							valori_pali[i] = valori_set[carta.value]
				i += 1
			punti[n].append(sum(valori_pali))
			
			punti[n].append(0)
			punti[n].append(0)
			for carta in carte_prese:
				if carta.suit == 0:
					punti[n][3] += 1
					if carta.value == 7:
						punti[n][2] = 1
			n += 1
		
		n=0
		while n < len(self.teams):
			self.teams[n][1].punti += self.teams[n][1].scope.scope
			punti[n].append(self.teams[n][1].scope.scope)
			punti[n].append(self.teams[n][1].scope.scope)
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

		widgets.show_summary(self.azzera, legenda, *colonne)
	
	def show_last_move(self):
		return 0
		
	def hide_last_move(self):
		pass

	#azzera la partita quando si finisce il mazzo
	def azzera(self):
		self.mazzo.populate()
		self.mazzo.mix()
		for giocatore in self.players:
			giocatore.carte_prese.reset()
			giocatore.scope.reset()
		if self.giocatore+1 < len(self.players):
			self.giocatore += 1
		else:
			self.giocatore = 0
		self.mano = 0
		massimo_punti = 0
		giocatore = -1
		n=0
		while n<len(self.teams):
			if self.teams[n][1].punti >= self.punti_vit:
				if self.teams[n][1].punti > massimo_punti:
					massimo_punti=self.teams[n][1].punti
					giocatore=n
				elif self.teams[n][1].punti == massimo_punti:
					giocatore=-1
			n+=1
		if giocatore >= 0:
			self.notifiche.notify(_('%s won!')%self.teams[giocatore][0],2000)
			self.end()
		else:
			self.start()
	
	def update_cards(self):
		self.mazzo.updated_cards()
		for card in self.carte_terra.get_list():
			card.draw_card()
		self.carte_terra.set_children_coords()
		for player in self.players:
			player.scope.draw()
			player.carte_prese.updated_cards()
			for card in player.mano.get_list():
				card.draw_card(player.ai)
			player.mano.set_children_coords()
	
	def destroy(self):
		self.mazzo.destroy()
		self.carte_terra.destroy_all()
		for player in self.players:
			player.mano.destroy_all()
			player.carte_prese.destroy()
			player.scope.destroy()