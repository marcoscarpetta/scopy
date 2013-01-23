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

from gi.repository import Gtk
import os
from base import *

Path=_('File')
Name=_('Play online...')

#multiplayer status images
stocks={'unavailable':Gtk.STOCK_NO,
	'available':Gtk.STOCK_YES,
	'playing':Gtk.STOCK_JUMP_TO}

def destroy(widget, response):
	widget.destroy()
	
def crea_win_online(self):
	self.win_online = Gtk.Window()
	self.win_online.set_title(_('Online game...'))
	self.win_online.set_transient_for(self.window)
	self.win_online.set_position(Gtk.WindowPosition.CENTER_ON_PARENT)
	self.win_online.connect('delete-event', self.hide)
	self.table_log=Gtk.Table(2,8,False)
	self.online_info = Gtk.Label()
	lab_usr=Gtk.Label(_('Username:'))
	lab_pwd=Gtk.Label(_('Password:'))
	lab_pwd_re=Gtk.Label(_('Repeat password:'))
	lab_re=Gtk.Label(_('Remember account:'))
	self.table_log.attach(self.online_info,0,2,7,8,Gtk.AttachOptions(0),Gtk.AttachOptions(0))
	self.table_log.attach(lab_usr,0,1,1,2,Gtk.AttachOptions(0),Gtk.AttachOptions(0))
	self.table_log.attach(lab_pwd,0,1,2,3,Gtk.AttachOptions(0),Gtk.AttachOptions(0))
	self.table_log.attach(lab_pwd_re,0,1,3,4,Gtk.AttachOptions(0),Gtk.AttachOptions(0))
	self.table_log.attach(lab_re,0,1,4,5,Gtk.AttachOptions(0),Gtk.AttachOptions(0))
	self.username=Gtk.Entry()
	self.password=Gtk.Entry()
	self.password.set_visibility(False)
	self.re_password=Gtk.Entry()
	self.re_password.set_visibility(False)
	self.remember=Gtk.CheckButton()
	self.table_log.attach(self.username,1,2,1,2,Gtk.AttachOptions(4),Gtk.AttachOptions(4))
	self.table_log.attach(self.password,1,2,2,3,Gtk.AttachOptions(4),Gtk.AttachOptions(4))
	self.table_log.attach(self.re_password,1,2,3,4,Gtk.AttachOptions(4),Gtk.AttachOptions(4))
	self.table_log.attach(self.remember,1,2,4,5,Gtk.AttachOptions(4),Gtk.AttachOptions(4))
	login=Gtk.Button.new_with_label(_('Login'))
	login.connect('pressed',self.show_login)
	reg=Gtk.Button.new_with_label(_('Register'))
	reg.connect('pressed',self.show_register)
	button=Gtk.Button.new_with_label(_('OK'))
	button.connect('pressed',self.logged)
	button.connect('activate',self.logged)
	button_re=Gtk.Button.new_with_label(_('OK'))
	button_re.connect('pressed',self.registred)
	self.password.set_property("activates-default",True)
	self.username.set_property("activates-default",True)
	self.spinner = Gtk.Spinner()
	self.table_log.attach(login,0,1,0,1,Gtk.AttachOptions(0),Gtk.AttachOptions(0))
	self.table_log.attach(reg,1,2,0,1,Gtk.AttachOptions(0),Gtk.AttachOptions(0))
	self.table_log.attach(button,1,2,5,6,Gtk.AttachOptions(0),Gtk.AttachOptions(0))
	self.table_log.attach(button_re,1,2,6,7,Gtk.AttachOptions(0),Gtk.AttachOptions(0))
	self.table_log.attach(self.spinner,0,1,5,6,Gtk.AttachOptions(0),Gtk.AttachOptions(0))
	self.win_login={True:[lab_usr,lab_pwd,self.username,self.password,lab_re,self.remember,button],
		False:[lab_pwd_re,login,reg,self.re_password,button_re,self.online_info,self.spinner]}
	self.win_reg={True:[lab_usr,lab_pwd,lab_pwd_re,self.username,self.password,self.re_password,lab_re,self.remember,button_re],
		False:[login,reg,button,self.spinner,self.online_info]}
	self.win_log_reg={True:[login,reg],
		False:[lab_pwd_re,lab_usr,lab_pwd,self.username,self.password,lab_re,self.remember,button,self.re_password,button_re,self.spinner,self.online_info]}
	self.win_online.add(self.table_log)
	button.set_can_default(True)
	button.grab_default()
def crea_win_multi(self):
	self.win_multi = Gtk.Window()
	self.win_multi.set_title(_('People'))
	self.win_multi.set_transient_for(self.window)
	self.win_multi.set_position(Gtk.WindowPosition.CENTER_ON_PARENT)
	self.win_multi.connect('delete-event', self.hide)
	self.win_multi.resize(400,300)
	table = Gtk.Table(2,2)
	self.players_list = Gtk.ListStore(str,int,int,str)
	tree_view = Gtk.TreeView.new_with_model(self.players_list)
	cell = Gtk.CellRendererText()
	column = Gtk.TreeViewColumn(_('User'), cell, text = 0)
	column.set_sort_column_id(0)
	tree_view.append_column(column)
	cell = Gtk.CellRendererText()
	column = Gtk.TreeViewColumn(_('Won'), cell, text = 1)
	column.set_sort_column_id(1)
	tree_view.append_column(column)
	cell = Gtk.CellRendererText()
	column = Gtk.TreeViewColumn(_('Lost'), cell, text = 2)
	column.set_sort_column_id(2)
	tree_view.append_column(column)
	cell = Gtk.CellRendererPixbuf()
	column = Gtk.TreeViewColumn(_('Status'), cell, stock_id = 3)
	column.set_sort_column_id(3)
	tree_view.append_column(column)
	tree_view.connect("row-activated",self.game_request)
	scrolledwindow = Gtk.ScrolledWindow()
	scrolledwindow.set_hexpand(True)
	scrolledwindow.set_vexpand(True)
	scrolledwindow.add(tree_view)
	table.attach(scrolledwindow,0,2,0,1)
	button=Gtk.Button()
	button.set_label(_('Disconnect'))
	button.connect('pressed',self.disconnect)
	table.attach(button,1,2,1,2,Gtk.AttachOptions(0),Gtk.AttachOptions(0))
	self.win_multi.add(table)
	
def show_win_online(self,wid=None):
	self.win_inizio.hide()
	if self.client != None:
		self.show_win_multi()
	elif 'username' in self.opzioni:
		for widget in self.win_login[True]:
			widget.show()
		for widget in self.win_login[False]:
			widget.hide()
		self.table_log.show()
		self.username.set_text(self.opzioni['username'])
		self.password.set_text(self.opzioni['password'])
		self.win_online.show()
	else:
		for widget in self.win_log_reg[True]:
			widget.show()
		for widget in self.win_log_reg[False]:
			widget.hide()
		self.table_log.show()
		self.win_online.show()
def show_login(self,wid=None):
	for widget in self.win_login[True]:
		widget.show()
	for widget in self.win_login[False]:
		widget.hide()
	self.win_online.show()
def show_register(self,wid=None):
	for widget in self.win_reg[True]:
		widget.show()
	for widget in self.win_reg[False]:
		widget.hide()
	self.win_online.show()
def show_win_multi(self):
	self.win_multi.show_all()
def show_win_request(self, req):
	pass

### FUNZIONI PER IL MULTIPLAYER ####
def logged(self,wid=None):
	if self.remember.get_active():
		self.opzioni['username']=self.username.get_text()
		self.opzioni['password']=self.password.get_text()
		self.save()
	self.spinner.start()
	self.spinner.show()
	self.client = sleekxmpp.ClientXMPP(self.username.get_text()+'@jabber.rootbash.com',self.password.get_text())
	self.client.register_plugin('xep_0030')
	self.client.register_plugin('xep_0004')
	self.client.register_plugin('xep_0060')
	self.client.register_plugin('xep_0199')
	self.client.add_event_handler('session_start', self.session_start)
	self.client.add_event_handler("changed_status", self.changed_status)
	self.client.add_event_handler("message", self.message)
	if self.client.connect():
		self.client.process(threaded=True)
		print "Done"
	else:
		print "Unable to connect."

def session_start(self, event):
	print 'connected'
	self.client.get_roster()
	self.client.send_presence()
	self.load_online_players()
	contatti = self.client.client_roster.keys()
	for player in self.online_players:
		if player != self.username.get_text()+'@jabber.rootbash.com' and player not in contatti:
			self.client.send_presence(pto=player, ptype='subscribe')
	treeiter = self.players_list.get_iter_first()
	ntree = treeiter
	while ntree:
		ntree=self.players_list.iter_next(treeiter)
		self.players_list.remove(treeiter)
		treeiter=ntree
	for contatto in contatti:
		self.players_list.append([contatto,self.online_players[contatto]['vinte'],self.online_players[contatto]['perse'],stocks[self.online_players[contatto]['stato']]])
	urllib2.urlopen('http://marcoscarpetta.altervista.org/scopy/insert.php?jid='+self.username.get_text()+'@jabber.rootbash.com')
	self.win_online.hide()
	self.spinner.stop()
	self.spinner.hide()
	self.show_win_multi()
def changed_status(self, presence):
	if presence['type'] not in ('subscribe', 'subscribed', 'unsubscribe', 'unsubscribed'):
		if presence['status'] != '':
			stato = presence['status']
		else:
			stato = presence['type']
		treeiter = self.players_list.get_iter_first()
		while treeiter:
			if self.players_list.get_value(treeiter,0) == presence['from'].bare:
				self.players_list.set_value(treeiter,3,stocks[stato])
				break
			treeiter=self.players_list.iter_next(treeiter)
def registred(self,wid=None):
	result=urllib2.urlopen('https://jabber.rootbash.com:9091/plugins/registration/sign-up.jsp?username='+
		self.username.get_text()+
		'&name=&email=&password='+
		self.password.get_text()+
		'&passwordConfirm='+
		self.re_password.get_text()+
		'&create=Create+Account')
	result = result.read()
	n=0
	while n < len(result):
		if result[n] == '<':
			if result[n:n+26] == '<div class="jive-success">':
				result = True
				break
		n=n+1
	if result == True:
		self.online_info.set_text(_('Account successfully created!'))
		self.online_info.show()
		self.logged()
	else:
		self.online_info.set_text(_('Registration error'))
		self.online_info.show()
def game_request(self, widget, path, view_column):
	statuses={Gtk.STOCK_NO:'unavailable',
		Gtk.STOCK_YES:'available',
		Gtk.STOCK_JUMP_TO:'playing'}
	if statuses[self.players_list[path][3]] not in ['playing','unavailable']:
		self.online_mode = True
		self.playing_user = self.players_list[path][0]
		self.client.send_presence(ptype='xa', pstatus='playing')
		self.show_win_inizio()
	else:
		self.show_dialog(_('Online game request'),
			(Gtk.STOCK_OK,0),
			_("You can't play with %(player)s because he is '%(game)s'" %{'player':self.players_list[path][0], 'game':statuses[self.players_list[path][3]]}))
def show_dialog(self, title,buttons,lab,msg=None):
	dialog = Gtk.Dialog(title,
		self.window,
		Gtk.DialogFlags.MODAL,
		buttons)
	label=Gtk.Label(lab)
	dialog.get_content_area().add(label)
	dialog.connect('response', self.response, msg)
	dialog.show_all()
def message(self, msg):
	body = msg['body']
	if msg['type'] in ('chat', 'normal'):
		if body[0:6] == 'scopy:':
			body = body[6:]
			if body[0:12] == 'game request':
				self.show_dialog(_('Online game request'),
					(Gtk.STOCK_YES,0,Gtk.STOCK_NO,1),
					_('%(player)s wants to play a "%(game)s" game with you.\nDo you accept the challenge?' %{'player':msg['from'].bare, 'game':body[12:]}),
					msg)
			if body[0:13] == 'game accepted':
				self.show_dialog(_('Online game request'),
					(_('Start game!'),0),
					_('%s accepted your game request.' %msg['from'].bare),
					msg)
			if body[0:] == 'game refused':
				self.online_mode = False
				self.show_dialog(_('Online game request'),
					(Gtk.STOCK_OK,0),
					_('%s refused your game request.' %msg['from'].bare),
					msg)
			if body[0:7] == 'partita':
				data = pickle.loads(body[7:])
				data[0].giocatore[0],data[0].giocatore[1] = data[0].giocatore[1],data[0].giocatore[0]
				data[0].ide = int(not data[0].ide)
				self.partita = data[0]
				#FIXME brutto
				try:
					a=self.carte[self.partita.giocatore[0].mano.carte[0].uid].get_x()
					if len(data)>1:
						self.gioca_computer(data[1])
				except:
					try:
						a=self.carte[self.partita.giocatore[1].mano.carte[0].uid].get_x()
						if len(data)>1:
							self.gioca_computer(data[1])
					except:
						self.sposta_carte()
						if len(data)>1:
							GLib.timeout_add(1000, self.gioca_computer, data[1])
			if body[0:9] == 'riepilogo':
				data = pickle.loads(body[9:])
				self.show_riepilogo(data)
def response(self, dialog, ide, msg):
	dialog.destroy()
	if msg != None:
		body = msg['body'][6:]
		if body[0:12] == 'game request':
			if ide == 0:
				self.online_mode = True
				self.playing_user = msg['from'].bare
				self.client.send_presence(ptype='xa', pstatus='playing')
				msg.reply('scopy:game accepted'+self.opzioni['nome']).send()
			if ide == 1:
				msg.reply('scopy:game refused').send()
		if body[0:13] == 'game accepted':
			self.crea_partita(body[13:])
			self.dichiara(self.partita.dai_carte())
			self.sposta_carte()
			if self.partita.ide == 1:
				self.client.send_message(mto=self.playing_user,
					mbody='scopy:partita'+pickle.dumps([self.partita]),
					mtype='chat')
def disconnect(self, wid=None, data=None):
	if self.client != None:
		a=self.client
		a.disconnect()
		self.client=None
		self.win_multi.hide()
		self.online_mode=False
def load_online_players(self):
	get = urllib2.urlopen('http://marcoscarpetta.altervista.org/scopy/get.php')
	import string
	data = string.split(get.read(),' ')
	n=0
	while n<len(data)/3:
		self.online_players[data[n*3]] = {'vinte':int(data[n*3+1]),'perse':int(data[n*3+2]),'stato':'unavailable'}
		n=n+1