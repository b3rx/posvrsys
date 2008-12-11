#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os, sys, shutil, zipfile

BASE_DIR = os.path.dirname(__file__)
OUT_DIR = os.path.join(BASE_DIR, 'dist')
B_DIR   = os.path.join(BASE_DIR, 'build')
GTK_ZIP = os.path.join('tools', 'windows', 'gtk', 'gtk_to_copy.zip')
INNO_SCRIPT = os.path.join('tools', 'config-inno.iss')
INNO_EXECUTABLE = '"c:\\Program Files\\Inno Setup 5\\ISCC.exe"'

class Unzip(object):
    def __init__(self, from_file, to_dir, verbose = False):
        
        fh = open(from_file, 'rb')
        z = zipfile.ZipFile(fh)
        for name in z.namelist():
            #print name
            outfile = open(name, 'wb')
            outfile.write(z.read(name))
            outfile.close()
        fh.close()



def delete_old_out_dir():
    if os.path.exists(OUT_DIR):
        shutil.rmtree(OUT_DIR)


def run_py2exe():
    # A hack really, but remember setup.py will run on import
    sys.argv.append('py2exe')
    import setup


def unzip_gtk():
    Unzip(GTK_ZIP, OUT_DIR)


def run_inno():
    os.system(INNO_EXECUTABLE + " " + INNO_SCRIPT)


def main():
    #Clean any mess we previously made
    delete_old_out_dir()
    # run py2exe
    run_py2exe()
    # put the GTK data files in the dist directory
    unzip_gtk()
    # build the single file installer
    #run_inno()
    # prevent the windows command prompt from just closing
    raw_input('Done..')

if __name__ == '__main__':
    
    main()