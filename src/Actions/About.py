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

from gettext import gettext as _
from gi.repository import Gtk,Gdk
from libscopyUI.base import *
import cairo

Path=_('Help')
Name=_('About')
	
def main(widget,app):
		about = Gtk.AboutDialog()
		about.set_title(_('About'))
		about.set_transient_for(app.window)
		about.set_position(Gtk.WindowPosition.CENTER_ON_PARENT)
		about.set_border_width(10)
		about.connect('delete-event', destroy)
		about.connect('close', destroy)
		about.connect('response', destroy)
		about.set_program_name('ScoPy')
		about.set_version(APP_VERSION)
		about.set_copyright('Copyright © 2011-2012 Marco Scarpetta <marcoscarpetta@mailoo.org>')
		about.set_comments(_('The italian card game "scopa"'))
		about.set_license_type(Gtk.License.GPL_3_0)
		about.set_website('http://scopy.sourceforge.net')
		about.set_authors(['Marco Scarpetta','Si ringrazia la comunità ubuntu-it e archlinux italia'])
		about.set_artists(['Marco Scarpetta',
			'crx (carte Piacentine)',
			'Scio Nescire (carte da Poker)',
			"00 ubuntu (carte 'Francitalia' e 'Scartini')",
			'vaillant (carte Siciliane)',
			'gikbuntu (carte Bergamasche)',
			'mapreri (carte Trevisane)',
			'Magog (sfondi, carte Toscane)'])
		about.set_translator_credits('Fitoschido \nSarahSlean \nMarti Bosch \nMarc Coll Carrillo')
		image = cairo.ImageSurface.create_from_png(percorso+'/data/icons/icona.png')
		icona = Gdk.pixbuf_get_from_surface(image,0,0,100,100)
		about.set_logo(icona)
		about.show()
