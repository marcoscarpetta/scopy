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

from gettext import gettext as _
from gi.repository import Gtk
from libscopyUI import base

Path=_('Help')
Name=_('About')

class Main():
	def __init__(self, app):
		self.dialog = Gtk.AboutDialog()
		self.dialog.set_title(_('About'))
		self.dialog.set_transient_for(app.window)
		self.dialog.set_position(Gtk.WindowPosition.CENTER_ON_PARENT)
		self.dialog.set_border_width(10)
		self.dialog.connect('delete-event', base.hide)
		self.dialog.connect('close', base.hide)
		self.dialog.connect('response', base.hide)
		self.dialog.set_program_name('ScoPy')
		self.dialog.set_version(base.APP_VERSION)
		self.dialog.set_copyright('Copyright © 2011-2013 Marco Scarpetta <marcoscarpetta@mailoo.org>')
		self.dialog.set_comments(_('The italian card game "scopa"'))
		self.dialog.set_license_type(Gtk.License.GPL_3_0)
		self.dialog.set_website('http://scopy.sourceforge.net')
		self.dialog.set_authors(['Marco Scarpetta','Si ringrazia la comunità ubuntu-it e archlinux italia'])
		self.dialog.set_artists(['Marco Scarpetta',
			'crx (carte Piacentine)',
			'Scio Nescire (carte da Poker)',
			"00 ubuntu (carte 'Francitalia' e 'Scartini')",
			'vaillant (carte Siciliane)',
			'gikbuntu (carte Bergamasche)',
			'mapreri (carte Trevisane)',
			'Magog (sfondi, carte Toscane)'])
		self.dialog.set_translator_credits('Adolfo Jayme Barrientos \nSarahSlean \nMarti Bosch \nMarc Coll Carrillo \nMichael Moroni \nAntonio Trande \nGenghis Khan \nStanislas Michalak \nAleksey Kabanov')
		self.dialog.set_logo(Gtk.IconTheme().load_icon("scopy", 128, 0))

	def main(self, widget):
		self.dialog.show()
