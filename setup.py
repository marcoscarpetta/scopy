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

src=[]
def list_files(p):
	for obj in os.listdir(p):
		if (p+'/'+obj) not in ['./debian','./scopy','./setup.py','./po','./.bzr','./data/scopy.desktop','./gettext_files'] and (p+'/'+obj)[0:8] != './scopy-':
			if os.path.isdir(p+'/'+obj):
				list_files(p+'/'+obj)
			else:
				src.append(['share/scopy/'+p[2:],[p[2:]+'/'+obj]])
list_files('.')
src.append(['share/applications',['data/scopy.desktop']])

setup(name='ScoPy',
	version='0.2',
	description="The italian card game 'scopa'",
	author='Marco Scarpetta',
	author_email='marcoscarpetta02@gmail.com',
	url='http://scopyfreesoftware.wordpress.com/',
	license='GPL v3',
	scripts=['scopy'],
	data_files=src,
	cmdclass={'install_data': InstallData}
	)
