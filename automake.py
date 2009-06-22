#!/usr/bin/env python
# -*- coding: utf-8 -*-

# package  : POSvrSys - PyGTK POS Video Rental System
# version  : $Id$
# copyright: Copyright (c) 2008-2009 Bertrand Kintanar <b3rxkintanar@gmail.com>
# license  : http://opensource.org/licenses/gpl-3.0.html
# url      : http://posvrsys.googlecode.com/
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
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
#   sqlite >= 2.3.5, sqlalchemy >= 0.5.0

__version__ = "$Rev$"
# $Source$

import sys
import shutil
from os import mkdir, system
from os.path import dirname, split, exists, join
from zipfile import ZipFile

BASE_DIR = dirname(__file__)
OUT_DIR  = join(BASE_DIR, 'dist')
B_DIR    = join(BASE_DIR, 'build')
GTK_ZIP  = join('tools', 'windows', 'gtk', 'gtk_to_copy.zip')
INNO_SCRIPT = join('tools', 'config-inno.iss')
INNO_EXECUTABLE = '"c:\\Program Files\\Inno Setup 5\\ISCC.exe"'

def path_name(name):
    
    return split(name)[0]


def file_name(name):

    return split(name)[1]

def file_names(names):
    
    return (name for name in names if file_name(name))

def path_names(names):

    return (name for name in names if path_name(name) and not file_name(name))
    
    
class Unzip(object):

    def __init__(self, from_file, to_dir, verbose = False):
        
        zipfile = ZipFile(from_file, 'r')
        names   = zipfile.namelist()
        
        for name in path_names(names):
            
            if not exists(join(to_dir, name)): 
            
                mkdir(join(to_dir, name))
        
        for name in file_names(names):
            
            outfile = file(join(to_dir, name), 'wb')
            outfile.write(zipfile.read(name))
            outfile.close()
        
def delete_old_out_dir():

    if exists(OUT_DIR):
    
        shutil.rmtree(OUT_DIR)
        
    if exists(B_DIR):
    
        shutil.rmtree(B_DIR)


def run_py2exe():

    # A hack really, but remember setup.py will run on import
    sys.argv.append('py2exe')
    import setup


def unzip_gtk():

    Unzip(GTK_ZIP, OUT_DIR)


def run_inno():

    system(INNO_EXECUTABLE + " " + INNO_SCRIPT)


def main():

    #Clean any mess we previously made
    delete_old_out_dir()
    # run py2exe
    run_py2exe()
    # put the GTK data files in the dist directory
    unzip_gtk()
    # build the single file installer
    run_inno()
    # prevent the windows command prompt from just closing
    raw_input('Done..')

if __name__ == '__main__':
    
    main()
