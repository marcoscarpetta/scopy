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

import core
import random

sette = core.carta(1,7)

class partita(core.partita):
	def __init__(self, nome, nc):
		self.giocatore = [core.giocatore(nome), core.giocatore(nc)]
		self.mazzo = core.mazzo(40)
		self.carte_terra = core.mazzo()
		self.mano = 0
		self.ide = random.randrange(2)
		self.ult_prende = 0
		self.punti_vit = 21
	def dai_carte(self):
		if len(self.mazzo.carte) != 0:
			self.trasf_carte(3, "giocatore", 0)
			self.trasf_carte(3, "giocatore", 1)
			ritorno = []
			for giocatore in self.giocatore:
				testo = []
				giocatore.scoperte = 0
				somma = 0
				for carta in giocatore.mano.carte:
					somma = somma + carta.valore
				if somma <= 9:
					giocatore.scope = giocatore.scope + 2
					giocatore.scoperte = 1
					testo.append(0)
				if giocatore.mano.carte[0].valore == giocatore.mano.carte[1].valore or giocatore.mano.carte[0].valore == giocatore.mano.carte[2].valore:
					if giocatore.mano.carte[1].valore != giocatore.mano.carte[2].valore:
						giocatore.scope = giocatore.scope + 3
						giocatore.scoperte = 1
						if testo != '':
							testo.append(2)
						else:
							testo.append(2)
					else:
						giocatore.scope = giocatore.scope + 7
						giocatore.scoperte = 1
						if testo != '':
							testo.append(1)
						else:
							testo.append(1)
				ritorno.append(testo)
			if self.mano == 0:
				self.trasf_carte(4, "terra")
				self.mano = self.mano+1
			return ritorno
	def gioca_computer(self):
		carte_mano = self.giocatore[1].mano.carte
		carte_terra = self.carte_terra.carte
		giocate = []
		no_prese = 1
		n = 0
		i = 0
		while n < len(carte_mano):
			prese_possibili = self.prese(carte_mano[n])
			if prese_possibili != [[]]:
				no_prese = 0
			for presa in prese_possibili:
				giocate.append([n, presa])
			n = n+1
		#se solo 1 giocata possibile
		if len(giocate) == 1:
			giocate[0][0] = carte_mano[giocate[0][0]].uid
			n=0
			while n < len(giocate[0][1]):
				giocate[0][1][n] = carte_terra[giocate[0][1][n]].uid
				n=n+1
			return giocate[0]
		#se non si puo' prendere
		elif no_prese == 1:
			ide_carte = range(len(carte_mano))
			migliore = [0,[],-20]
			for ide_carta in ide_carte:
				valore = 0
				n = 0
				#2 carte uguali
				for carta in carte_mano:
					if carta.valore == carte_mano[ide_carta].valore:
						n = n + 1
				if n >= 2:
					valore = valore + 1
				#non denari
				if carte_mano[ide_carta].palo != 0:
					valore = valore + 1
				#non 7
				if carte_mano[ide_carta].valore != 7:
					valore = valore + 1
				n = 0
				#carta piu' bassa
				for carta in carte_mano:
					if carta.valore > carte_mano[ide_carta].valore:
						n = n + 1
				if n == len(carte_mano):
					valore = valore + 1
				#non 7 a terra
				if len(self.prese(sette)) != 0:
					valore = valore - 1
				#presa dopo
				for carta in carte_mano:
					if carta != carte_mano[ide_carta]:
						if len(self.prese(carta)) != 0:
							valore = valore + 1
				#scopa avversario
				valore_terra = 0
				for carta in carte_terra:
					valore_terra = valore_terra + carta.valore
				valore_terra = valore_terra + carte_mano[ide_carta].valore
				if valore_terra <= 10:
					valore = valore - 6
				#carte avversario conosciute
				if self.giocatore[0].scoperte == 1:
					prese = 0
					for carta in self.giocatore[0].mano.carte:
						prese = prese + len(self.prese(carta, self.carte_terra.carte+[carte_mano[ide_carta]]))
					valore = valore - prese
				if valore > migliore[2]:
					migliore[0], migliore[2] = ide_carta, valore
			migliore[0] = carte_mano[migliore[0]].uid
			n=0
			while n < len(migliore[1]):
				migliore[1][n] = carte_terra[migliore[1][n]].uid
				n=n+1
			return migliore[0:2]
		
		else:
			migliore = [0,[],-20]
			for giocata in giocate:
				valore = 0
				#scopa
				if len(giocata[1]) == len(carte_terra):
					valore = valore + 20
				valore_terra = 0
				#scopa avversario
				carte_da_lasciare=[]
				for ide_carta in range(len(carte_terra)):
					if not ide_carta in giocata[1]:
						valore_terra = valore_terra + carte_terra[ide_carta].valore
						carte_da_lasciare.append(carte_terra[ide_carta])
				if giocata[1] == []:
					valore_terra = valore_terra + carte_mano[giocata[0]].valore
					carte_da_lasciare.append(carte_mano[giocata[0]])
				if valore_terra <= 10:
					valore = valore - 6
				if self.giocatore[0].scoperte == 1:
					prese = 0
					for carta in self.giocatore[0].mano.carte:
						prese = prese + len(self.prese(carta, carte_da_lasciare))
					valore = valore - prese
				if giocata[1] == []:
					#non denaro
					if carte_mano[giocata[0]].palo != 0:
						valore = valore + 1
					#non 7
					if carte_mano[giocata[0]].valore != 7:
						valore = valore + 1
					n = 0
					#carta piu' bassa
					for carta in carte_mano:
						if carta.valore > carte_mano[giocata[0]].valore:
							n = n + 1
					if n == len(carte_mano):
						valore = valore + 1
				else:
					carte_da_prendere=[]
					carte_da_prendere.append(carte_mano[giocata[0]])
					for ide_carta in giocata[1]:
						carte_da_prendere.append(carte_terra[ide_carta])	
					valore = valore + len(carte_da_prendere)
					for carta in carte_da_prendere:
						if carta.palo == 0:
							valore = valore + 3
						if carta.valore == 7:
							valore = valore + 4
							if carta.palo == 0:
								valore = valore + 20
						if carta.valore == 6:
							valore = valore + 2
						if carta.valore == 1:
							valore = valore + 1
				if valore > migliore[2]:
					migliore[0], migliore[1], migliore[2] = giocata[0], giocata[1], valore
			migliore[0] = carte_mano[migliore[0]].uid
			n=0
			while n < len(migliore[1]):
				migliore[1][n] = carte_terra[migliore[1][n]].uid
				n=n+1
			return migliore[0:2]
