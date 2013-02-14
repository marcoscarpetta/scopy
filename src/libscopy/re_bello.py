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

import core
sette = core.carta(1,7)
valori_set = [0, 16, 12, 13, 14, 15, 18, 21, 10, 10, 10]
class partita(core.partita):
	#valuta la migliore presa che il computer puo' fare
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
				#non re bello
				if carte_mano[ide_carta].valore != 10 and carte_mano[ide_carta].palo != 0:
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
				for ide_carta in range(len(carte_terra)):
					if not ide_carta in giocata[1]:
						valore_terra = valore_terra + carte_terra[ide_carta].valore
				if giocata[1] == []:
					valore_terra = valore_terra + carte_mano[giocata[0]].valore
				if valore_terra <= 10:
					valore = valore - 6
				if giocata[1] == []:
					#non denaro
					if carte_mano[giocata[0]].palo != 0:
						valore = valore + 1
					#non 7
					if carte_mano[giocata[0]].valore != 7:
						valore = valore + 1
					#non re bello
					if carte_mano[giocata[0]].valore != 10 and carte_mano[giocata[0]].palo != 0:
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
						if carta.valore == 10 and carta.palo == 0:
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
		#assegna il re bello
		for carta in self.giocatore[0].carte_prese.carte:
			if carta.palo == 0 and carta.valore == 10:
				self.giocatore[0].punti = self.giocatore[0].punti + 1
				parziale[0] = parziale[0] + 1
				ritorno['Re Bello'] = [1,0]
		for carta in self.giocatore[1].carte_prese.carte:
			if carta.palo == 0 and carta.valore == 10:
				self.giocatore[1].punti = self.giocatore[1].punti + 1
				parziale[1] = parziale[1] + 1
				ritorno['Re Bello'] = [0,1]
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
