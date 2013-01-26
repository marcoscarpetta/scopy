#!/usr/bin/python

##
# Project: ScoPy - The italian card game 'scopa'
# Author: Marco Scarpetta <marcoscarpetta02@gmail.com>
# Copyright: 2011 Marco Scarpeta
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
from distutils.core import setup
from distutils.command.install_data import install_data
from distutils.dep_util import newer
from distutils.log import info
import glob
import os
import sys
	
class InstallData(install_data):
  def run (self):
    self.data_files.extend (self._compile_po_files())
    install_data.run(self)

  def _compile_po_files(self):
    data_files = []

    # Don't install language files on win32
    if sys.platform == 'win32':
      return data_files

    PO_DIR = 'po'
    for po in glob.glob (os.path.join (PO_DIR,'*.po')):
      lang = os.path.basename(po[:-3])
      mo = os.path.join('build', 'mo', lang, 'scopy.mo')

      directory = os.path.dirname(mo)
      if not os.path.exists(directory):
        info('creating %s' % directory)
        os.makedirs(directory)

      if newer(po, mo):
        # True if mo doesn't exist
        cmd = 'msgfmt -o %s %s' % (mo, po)
        info('compiling %s -> %s' % (po, mo))
        if os.system(cmd) != 0:
          raise SystemExit('Error while running msgfmt')

        dest = os.path.dirname(os.path.join('share', 'locale',
          lang, 'LC_MESSAGES', 'scopy.mo'))
        data_files.append((dest, [mo]))

    return data_files

setup(name='ScoPy',
	version='0.5',
	description="The italian card game 'scopa'",
	author='Marco Scarpetta',
	author_email='marcoscarpetta@mailoo.org',
	url='http://scopy.sourceforge.net/',
	license='GPL v3',
	scripts=['scopy'],
	data_files=(('share/applications', ['data/scopy.desktop']),
		('share/scopy/data/images/tappeti', glob.glob('data/images/tappeti/*')),
		('share/scopy/data/images/carte/Siciliane', glob.glob('data/images/carte/Siciliane/*')),
		('share/scopy/data/images/carte/Bergamasche', glob.glob('data/images/carte/Bergamasche/*')),
		('share/scopy/data/images/carte/Trevisane', glob.glob('data/images/carte/Trevisane/*')),
		('share/scopy/data/images/carte/Scartini', glob.glob('images/carte/Scartini/*')),
		('share/scopy/data/images/carte/Francitalia', glob.glob('data/images/carte/Francitalia/*')),
		('share/scopy/data/images/carte/Piacentine', glob.glob('data/images/carte/Piacentine/*')),
		('share/scopy/data/images/carte/Napoletane', glob.glob('data/images/carte/Napoletane/*')),
		('share/scopy/data/images/carte/Poker', glob.glob('data/images/carte/Poker/*')),
		('share/scopy/data/images/carte/Toscane', glob.glob('data/images/carte/Toscane/*')),
		('share/scopy/data/icons', glob.glob('data/icons/*')),
		('share/scopy/data/ui', glob.glob('data/ui/*')),
		('share/scopy/doc/en', glob.glob('doc/en/*')),
		('share/scopy/doc/it', glob.glob('doc/it/*')),
		('share/scopy/doc', ['doc/Copyright']),
		('share/scopy/src/Actions', glob.glob('src/Actions/*')),
		('share/scopy/src/libscopy', glob.glob('src/libscopy/*')),
		('share/scopy/src/libscopyUI', glob.glob('src/libscopyUI/*')),
		('share/scopy/src', ['src/scopy.py'])
		)
	cmdclass={'install_data': InstallData}
	)
