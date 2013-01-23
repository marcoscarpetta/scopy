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

valori_set = [0, 16, 12, 13, 14, 15, 18, 21, 10, 10, 10]

class partita(core.partita):
	def __init__(self, nome, nc):
		self.giocatore = [core.giocatore(nome), core.giocatore(nc)]
		self.mazzo = core.mazzo(40)
		self.carte_terra = core.mazzo()
		self.mano = 0
		self.ide = random.randrange(2)
		self.ult_prende = 0
		self.punti_vit = 51
	def prese(self, carta):
		try:
			valore = carta.sette
		except:
			valore = carta.valore
		carte = self.carte_terra.carte
		prese = []
		n = 0
		i = 0
		while n < len(carte):
			if valore == carte[n].valore:
				prese.append([n])
			if valore+carte[n].valore==15:
				prese.append([n])
			if carte[n].valore == 1:
				i=1
			n = n+1
		if valore == 1 and len(prese) == 0 and i==0:
			prese.append(range(len(carte)))
		lista_combinazioni = self.combinazioni(range(len(carte)))
		for combinazione in lista_combinazioni:
			somma = 0
			for elemento in combinazione:
				somma = somma + carte[elemento].valore
			if somma == valore:
				prese.append(combinazione)
			if (somma+valore) == 15:
				prese.append(combinazione)
		if prese == []:
			return [[]]
		else:			
			return prese
	def dai_carte(self):
		if len(self.mazzo.carte) != 0:
			self.trasf_carte(3, "giocatore", 0)
			self.trasf_carte(3, "giocatore", 1)
			ritorno = []
			for giocatore in self.giocatore:
				testo = []
				giocatore.scoperte = 0
				somma = 0
				sette = 0
				for carta in giocatore.mano.carte:
					somma = somma + carta.valore
					if carta.valore==7 and carta.palo==0:
						sette=1
						ide_sette=giocatore.mano.carte.index(carta)
						carte_w_sette = []
						for n in range(3):
							if n != ide_sette:
								carte_w_sette.append(giocatore.mano.carte[n])
				if somma <= 9:
					giocatore.scope = giocatore.scope + 3
					giocatore.scoperte = 1
					testo.append(0)
				elif sette==1:
					if somma-6 <= 9:
						giocatore.scope = giocatore.scope + 3
						giocatore.scoperte = 1
						testo.append(0)
						giocatore.mano.carte[ide_sette].sette=1
				if giocatore.mano.carte[0].valore == giocatore.mano.carte[1].valore == giocatore.mano.carte[2].valore:
					giocatore.scope = giocatore.scope + 10
					giocatore.scoperte = 1
					testo.append(1)
				elif sette==1:
					if carte_w_sette[0].valore == carte_w_sette[1].valore:
						giocatore.scope = giocatore.scope + 10
						giocatore.scoperte = 1
						testo.append(1)
						giocatore.mano.carte[ide_sette].sette=carte_w_sette[0].valore
				ritorno.append(testo)
			if self.mano == 0:
				self.trasf_carte(4, "terra")
			self.mano = self.mano+1
			return ritorno
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
		denari = [[],[]]
		n = 0
		while n < 2:
			for carta in self.giocatore[n].carte_prese.carte:
				if carta.palo == 0:
					denari[n].append(carta.valore)
			n = n+1
		if len(denari[0]) > len(denari[1]):
			self.giocatore[0].punti = self.giocatore[0].punti + 1
			parziale[0] = parziale[0] + 1
		elif len(denari[1]) > len(denari[0]):
			self.giocatore[1].punti = self.giocatore[1].punti + 1
			parziale[1] = parziale[1] + 1
		denari[0].sort()
		denari[1].sort()
		n=0
		while n < 2:
			if len(denari[n]) != 0:
				punti = 0
				i=1
				while i == denari[n][i-1]:
					punti = punti + 1
					i=i+1
				if punti >=3:
					self.giocatore[n].punti = self.giocatore[n].punti + punti
					self.giocatore[n].scope = self.giocatore[n].scope + punti
				punti = 0
				i=10
				while i == denari[n][i-11]:
					punti = punti + 1
					i=i-1
				if punti >=3:
					self.giocatore[n].punti = self.giocatore[n].punti + punti
					self.giocatore[n].scope = self.giocatore[n].scope + punti
				n=n+1
		ritorno['Denari'] = [len(denari[0]),len(denari[1])]
		#assegna le scope
		self.giocatore[0].punti = self.giocatore[0].punti + self.giocatore[0].scope
		parziale[0] = parziale[0] + self.giocatore[0].scope
		self.giocatore[1].punti = self.giocatore[1].punti + self.giocatore[1].scope
		parziale[1] = parziale[1] + self.giocatore[1].scope
		ritorno['Scope'] = [self.giocatore[0].scope, self.giocatore[1].scope]
		ritorno['Parziale'] = parziale
		return ritorno
