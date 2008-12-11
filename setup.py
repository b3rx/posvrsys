#!/usr/bin/env python
# -*- coding: utf-8 -*-

# POSvrSys - PyGTK POS Video Rental System
# Copyright (C) 2008 Bertrand Kintanar <b3rxkintanar@gmail.com>
# http://posvrsys.googlecode.com/
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Library General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.
#
# If you find any bugs or have any suggestions email: b3rxkintanar@gmail.com
# URL: http://posvrsys.googlecode.com/
#
# POSvrSys needs the following to function properly:
#   python >= 2.5.1, gtk >= 2.12.9, pygtk >= 2.12.2, 
#   sqlite >= 2.3.5, sqlalchemy >= 0.5.0rc4

from distutils.core import setup
import os
import py2exe

import config

setup(
    name = config.APP_NAME, 
    version = config.__version__, 
    license = config.__license__, 
    author = 'Bertrand Son Kintanar', 
    author_email = '<b3rxkintanar@gmail.com>', 
    scripts=['posvrsys.py'],
    windows=[
        {
            'script': 'posvrsys.py',
            'icon_resources': [(1, os.path.join('img', 'logo.ico'))],
        }
    ],
    data_files=[
        ('glade', [os.path.join('glade', 'posvrsys.glade'),
                   os.path.join('glade', 'logo.ico')]),
        ('img', [
            os.path.join('img', 'rentals.png'),
            os.path.join('img', 'inventory.png'),
            os.path.join('img', 'customers.png'),
            os.path.join('img', 'transactions.png'),
            os.path.join('img', 'reports.png'),
            os.path.join('img', 'maintenance.png'),
            os.path.join('img', 'dayend.png'),]
         ),
    ],
    options = {
        'py2exe' : {
            'packages': 'encodings, sqlalchemy',
            'includes': 'cairo, pango, pangocairo, atk, gobject',
        },
        'sdist': {
            'formats': 'zip',
        }
    }
)