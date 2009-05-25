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

_ = lambda x : x

from config import *
from config import __appversion__

try:
    
    import base64
    import datetime
    import gettext
    import gobject
    import locale
    import os
    import re
    import sys
    
except ImportError, e:
    
    print _("Import error POSvsSys cannot start:"), e
    
    sys.exit(1)

try:
    
    import pygtk
    pygtk.require20()
    import gtk
    import gtk.glade
    
    try:
        
        assert gtk.ver >= (2, 14, 1)
    
    except AssertionError:
        
        print _("%s requires GTK+ 2.14.1 or higher, but %s was found") \
            % (APP_NAME, gtk.ver)
        
        sys.exit(1)
    
    if DEBUG:
        
        print _("Checking pygtk 2.0............. Found")
        print _("Checking gtk+ 2.14.1........... Found")
        print _("Checking glade................. Found")
        
except ImportError, e:
    
    print _("Import error POSvsSys cannot start:"), e
    
    sys.exit(1)
    
from sql import *
from datepicker import CalendarEntry

session = checkDatabase('posvrsys.sqlite')

"""Column IDs"""
COL_OBJECT      = 0
COL_OBJECT_TYPE = 1
COL_CODE        = 2
COL_TITLE       = 3
COL_NAME        = 3
COL_GENRES      = 4
COL_NUMBER      = 4
COL_ADDRESS     = 5
COL_TYPE        = 5
COL_CITY        = 6
COL_PROV        = 7
COL_ZIP         = 8
COL_COUNTRY     = 9

class TVColumn(object):
    """This is a class that represents a column in the todo tree.
    It is simply a helper class that makes it easier to inialize the
    tree."""

    def __init__(self, ID, type, name, pos, visible=False, cellrenderer=None):
        """
        @param ID - int - The Columns ID
        @param type - int  - A gobject.TYPE_ for the gtk.TreeStore
        @param name - string - The name of the column
        @param pos - int - The index of the column.
        @param visible - boolean - Is the column visible or not?
        @param cellrenderer - gtk.CellRenderer - a constructor function
        for the column
        """
        self.ID = ID
        self.type = type
        self.name = name
        self.pos = pos
        self.visible = visible
        self.cellrenderer = cellrenderer
        self.colour = 0
        
    def __str__(self):
        
        return "<TVColumn object: ID = %s type = %s name = %s pos = %d visible = %s cellrenderer = %s>" % (self.ID, self.type, self.name, self.pos, self.visible, self.cellrenderer)
    
class POSvrSys(object):

    def __init__(self):
        
        if DEBUG:
            
            print _("Initializing"), APP_NAME
            
        #Get the local path
        self.local_path = os.path.realpath(os.path.dirname(sys.argv[0]))
        #Translation stuff
        self.initialize_translation()
        
        #Set the Glade file
        self.gladefile = os.path.join(self.local_path, "glade", "posvrsys.glade")
        
        #Get the Main Widget Tree
        self.wTree = gtk.glade.XML(self.gladefile, "mainWindow")
        self.main_window = self.wTree.get_widget("mainWindow")
        
        #Initialize some widgets
        self.initialize_widgets()
        
        if LOGIN:
            
            self.security()
            
        self.main_window.set_title(APP_NAME + " " + __appversion__) 
        self.main_window.maximize()
        
        #Connect with yourself
        self.wTree.signal_autoconnect(self)
        
        self.reCuEntry.grab_focus()
        self.main_window.show_all()
        
    #***************************************************************************
    # Initialize
    #***************************************************************************
    def initialize_widgets(self):
        
        self.notebook       = self.wTree.get_widget("notebook")
        
        self.reNotebook     = self.wTree.get_widget("reNotebook")
        self.reCuEntry      = self.wTree.get_widget("reCuEntry")
        self.reInEntry      = self.wTree.get_widget("reInEntry")
        self.reInAlertLabel = self.wTree.get_widget("reInAlertLabel")
        
        self.root_window = self.main_window.get_root_window()
        
        self.create_buttonImages()
        self.create_statusbar()
        self.create_aboutDialog()
        self.create_reCuListstore()
        self.create_reInListstore()
        self.create_inAddEditDialog()
        self.create_cuAddEditDialog()
        
    def initialize_translation(self):
        """This function initializes the possible translations"""
        
        # Init the list of languages to support
        langs = []
        
        #Check the default locale
        lc, encoding = locale.getdefaultlocale()
        
        if (lc):
            #If we have a default, it's the first in the list
            langs = [lc]
            
        # Now lets get all of the supported languages on the system
        language = os.environ.get('LANGUAGE', None)
        
        if (language):
            """
            language comes back something like en_CA:en_US:en_GB:en
            on linuxy systems, on Win32 it's nothing, so we need to
            split it up into a list
            """
            
            langs += language.split(":")
            
        """
        Now add on to the back of the list the translations that we
        know that we have, our defaults
        """
        
        langs += ["en_CA", "en_US"]
        
        """
        Now langs is a list of all of the languages that we are going
        to try to use.  First we check the default, then what the system
        told us, and finally the 'known' list
        """
        
        gettext.bindtextdomain(APP_NAME, self.local_path)
        gettext.textdomain(APP_NAME)
        
        # Get the language to use
        self.lang = gettext.translation(APP_NAME, self.local_path
                                        , languages=langs, fallback = True)
        
        """
        Install the language, map _() (which we marked our
        strings to translate with) to self.lang.gettext() which will
        translate them.
        """
        gettext.install(APP_NAME, self.local_path)
        
    #***************************************************************************
    # Create Widgets
    #***************************************************************************
    def create_buttonImages(self):
        
        self.reButton = self.wTree.get_widget("reButton")
        self.inButton = self.wTree.get_widget("inButton")
        self.cuButton = self.wTree.get_widget("cuButton")
        self.trButton = self.wTree.get_widget("trButton")
        self.rpButton = self.wTree.get_widget("rpButton")
        self.daButton = self.wTree.get_widget("daButton")
        self.maButton = self.wTree.get_widget("maButton")
        
        reImageBox = self.add_image(self, "rentals.png", _("_Rentals"))
        inImageBox = self.add_image(self, "inventory.png", _("_Inventory"))
        cuImageBox = self.add_image(self, "customers.png", _("_Customers"))
        trImageBox = self.add_image(self, "transactions.png", _("_Transactions"))
        rpImageBox = self.add_image(self, "reports.png", _("Rep_orts"))
        maImageBox = self.add_image(self, "maintenance.png", _("_Maintenance"))
        daImageBox = self.add_image(self, "dayend.png", _("_Day-End"))
        
        self.reButton.set_image(reImageBox)
        self.inButton.set_image(inImageBox)
        self.cuButton.set_image(cuImageBox)
        self.trButton.set_image(trImageBox)
        self.rpButton.set_image(rpImageBox)
        self.maButton.set_image(maImageBox)
        self.daButton.set_image(daImageBox)
        
        reImageBox.show()
        inImageBox.show()
        cuImageBox.show()
        trImageBox.show()
        rpImageBox.show()
        maImageBox.show()
        daImageBox.show()
        
    def create_statusbar(self):
        
        self.statusbar = self.wTree.get_widget("statusbar")
        
        self.context_id = self.statusbar.get_context_id("POSvrSys")
        self.statusbar.push(self.context_id, _("Welcome to %s %s") \
            % (APP_NAME, __appversion__))
        
    def create_inListstore(self):
        
        self.inListstore_columns = [
            TVColumn(COL_OBJECT, gobject.TYPE_PYOBJECT, "object", 0)
            , TVColumn(COL_OBJECT_TYPE, gobject.TYPE_INT, "object_type", 1)
            , TVColumn(COL_CODE, gobject.TYPE_STRING, _("Code"), 2, True, gtk.CellRendererText())
            , TVColumn(COL_TITLE, gobject.TYPE_STRING, _("Title"), 3, True, gtk.CellRendererText())
            , TVColumn(COL_GENRES, gobject.TYPE_STRING, _("Genres"), 4, True, gtk.CellRendererText())
            , TVColumn(COL_TYPE, gobject.TYPE_STRING, _("Director"), 5, True, gtk.CellRendererText())
        ]
        
        """Called when we want to initialize the tree.
        """
        tree_type_list = [] #For creating the TreeStore
        self.__column_dict = {} #For easy access later on

        #Get the treeView from the widget Tree
        self.inTreeview = self.wTree.get_widget("inTreeview")
        #Make it so that the colours of each row can alternate
        self.inTreeview.set_rules_hint(True)

        # Loop through the columns and initialize the Tree
        for item_column in self.inListstore_columns:
            #Add the column to the column dict
            self.__column_dict[item_column.ID] = item_column
            #Save the type for gtk.TreeStore creation
            tree_type_list.append(item_column.type)
            #is it visible?
            if (item_column.visible):
                #Create the Column
                column = gtk.TreeViewColumn(item_column.name
                    , item_column.cellrenderer
                    , text=item_column.pos)
                
                # Set the column to expand if it is the column Title
                column.set_expand(item_column.name == _("Title"))
                
                column.set_resizable(True)
                column.set_sort_column_id(item_column.pos)
                self.inTreeview.append_column(column)
                
        #Create the gtk.TreeStore Model to use with the inTreeview
        self.inListstore = gtk.ListStore(*tree_type_list)
        #Attache the model to the treeView
        self.inTreeview.set_model(self.inListstore)
        
        self.populate_inListstore()
        
    def create_inGenreListstore(self):
        
        self.inGenresListstore_columns = [
            TVColumn(COL_OBJECT, gobject.TYPE_PYOBJECT, "object", 0)
            , TVColumn(COL_OBJECT_TYPE, gobject.TYPE_INT, "object_type", 1)
            , TVColumn(COL_CODE, gobject.TYPE_STRING, _("Genre"), 2, True, gtk.CellRendererText())
        ]
        
        """Called when we want to initialize the tree.
        """
        tree_type_list = [] #For creating the TreeStore
        __column_dict  = {} #For easy access later on
        
        for item_column in self.inGenresListstore_columns:
            
            tree_type_list.append(item_column.type)
            
        #Save the type for gtk.TreeStore creation
        self.inGenresAddEditListstore = gtk.ListStore(*tree_type_list)
        
        # Loop through the columns and initialize the Tree
        for item_column in self.inGenresListstore_columns:
            #Add the column to the column dict
            __column_dict[item_column.ID] = item_column
            
            #is it visible?
            if (item_column.visible):
                #Create the Column
                column = gtk.TreeViewColumn(
                    item_column.name, 
                    item_column.cellrenderer, 
                    text=item_column.pos
                )
                
                column.set_resizable(True)
                column.set_sort_column_id(item_column.pos)
                self.inGenresTreeview.append_column(column)
                
        self.inGenresAddEditListstore.set_name('inGenresAddEditListstore')
        self.inGenresTreeview.set_model(self.inGenresAddEditListstore)
        #self.inGenresTreeview.get_selection().set_mode(gtk.SELECTION_MULTIPLE)
        
    def create_inCastListstore(self):
        
        self.inCastsListstore_columns = [
            TVColumn(COL_OBJECT, gobject.TYPE_PYOBJECT, "object", 0)
            , TVColumn(COL_OBJECT_TYPE, gobject.TYPE_INT, "object_type", 1)
            , TVColumn(COL_CODE, gobject.TYPE_STRING, _("Full Name"), 2, True, gtk.CellRendererText())
        ]
        
        """Called when we want to initialize the tree.
        """
        tree_type_list = [] #For creating the TreeStore
        __column_dict  = {} #For easy access later on
        
        for item_column in self.inCastsListstore_columns:
            
            tree_type_list.append(item_column.type)
            
        #Save the type for gtk.TreeStore creation
        self.inCastsAddEditListstore = gtk.ListStore(*tree_type_list)
        
        # Loop through the columns and initialize the Tree
        for item_column in self.inCastsListstore_columns:
            #Add the column to the column dict
            __column_dict[item_column.ID] = item_column
            
            #is it visible?
            if (item_column.visible):
                #Create the Column
                column = gtk.TreeViewColumn(
                    item_column.name, 
                    item_column.cellrenderer, 
                    text=item_column.pos
                )
                
                column.set_resizable(True)
                column.set_sort_column_id(item_column.pos)
                self.inCastsTreeview.append_column(column)
                
        self.inCastsAddEditListstore.set_name('inCastsAddEditListstore')
        self.inCastsTreeview.set_model(self.inCastsAddEditListstore)
        #self.inGenresTreeview.get_selection().set_mode(gtk.SELECTION_MULTIPLE)
        
    def create_inWriterListstore(self):
        
        self.inWritersListstore_columns = [
            TVColumn(COL_OBJECT, gobject.TYPE_PYOBJECT, "object", 0)
            , TVColumn(COL_OBJECT_TYPE, gobject.TYPE_INT, "object_type", 1)
            , TVColumn(COL_CODE, gobject.TYPE_STRING, _("Full Name"), 2, True, gtk.CellRendererText())
        ]
        
        """Called when we want to initialize the tree.
        """
        tree_type_list = [] #For creating the TreeStore
        __column_dict  = {} #For easy access later on
        
        for item_column in self.inWritersListstore_columns:
            
            tree_type_list.append(item_column.type)
            
        #Save the type for gtk.TreeStore creation
        self.inWritersAddEditListstore = gtk.ListStore(*tree_type_list)
        
        # Loop through the columns and initialize the Tree
        for item_column in self.inWritersListstore_columns:
            #Add the column to the column dict
            __column_dict[item_column.ID] = item_column
            
            #is it visible?
            if (item_column.visible):
                #Create the Column
                column = gtk.TreeViewColumn(
                    item_column.name, 
                    item_column.cellrenderer, 
                    text=item_column.pos
                )
                
                column.set_resizable(True)
                column.set_sort_column_id(item_column.pos)
                self.inWritersTreeview.append_column(column)
                
        self.inWritersAddEditListstore.set_name('inWritersAddEditListstore')
        self.inWritersTreeview.set_model(self.inWritersAddEditListstore)
        #self.inGenresTreeview.get_selection().set_mode(gtk.SELECTION_MULTIPLE)
        
    def create_cuListstore(self):
        
        self.cuListstore_columns = [
            TVColumn(COL_OBJECT, gobject.TYPE_PYOBJECT, "object", 0)
            , TVColumn(COL_OBJECT_TYPE, gobject.TYPE_INT, "object_type", 1)
            , TVColumn(COL_CODE, gobject.TYPE_STRING, _("Code"), 2, True, gtk.CellRendererText())
            , TVColumn(COL_NAME, gobject.TYPE_STRING, _("Name"), 3, True, gtk.CellRendererText())
            , TVColumn(COL_NUMBER, gobject.TYPE_STRING, _("Contact Number"), 4, True, gtk.CellRendererText())
            , TVColumn(COL_ADDRESS, gobject.TYPE_STRING, _("Address"), 5, True, gtk.CellRendererText())
            , TVColumn(COL_CITY, gobject.TYPE_STRING, _("City/Town"), 6, True, gtk.CellRendererText())
            , TVColumn(COL_PROV, gobject.TYPE_STRING, _("State/Province"), 7, True, gtk.CellRendererText())
            , TVColumn(COL_ZIP, gobject.TYPE_STRING, _("Zip Code"), 8, True, gtk.CellRendererText())
            , TVColumn(COL_COUNTRY, gobject.TYPE_STRING, _("Country"), 9, True, gtk.CellRendererText())
        ]
        
        """Called when we want to initialize the tree.
        """
        tree_type_list = [] #For creating the TreeStore
        self.__cu_column_dict = {} #For easy access later on

        #Get the treeView from the widget Tree
        self.cuTreeview = self.wTree.get_widget("cuTreeview")
        #Make it so that the colours of each row can alternate
        self.cuTreeview.set_rules_hint(True)

        # Loop through the columns and initialize the Tree
        for item_column in self.cuListstore_columns:
            #Add the column to the column dict
            self.__cu_column_dict[item_column.ID] = item_column
            #Save the type for gtk.TreeStore creation
            tree_type_list.append(item_column.type)
            #is it visible?
            if (item_column.visible):
                #Create the Column
                column = gtk.TreeViewColumn(item_column.name
                    , item_column.cellrenderer
                    , text=item_column.pos)
                
                column.set_resizable(True)
                column.set_sort_column_id(item_column.pos)
                self.cuTreeview.append_column(column)
                
        #Create the gtk.TreeStore Model to use with the inTreeview
        self.cuListstore = gtk.ListStore(*tree_type_list)
        #Attache the model to the treeView
        self.cuTreeview.set_model(self.cuListstore)
        
        self.populate_cuListstore()
        
    def create_reCuListstore(self):
        
        self.reCuListstore_columns = [
            TVColumn(COL_OBJECT, gobject.TYPE_PYOBJECT, "object", 0)
            , TVColumn(COL_OBJECT_TYPE, gobject.TYPE_INT, "object_type", 1)
            , TVColumn(COL_CODE, gobject.TYPE_STRING, _("Code"), 2, True, gtk.CellRendererText())
            , TVColumn(COL_NAME, gobject.TYPE_STRING, _("Name"), 3, True, gtk.CellRendererText())
            , TVColumn(COL_NUMBER, gobject.TYPE_STRING, _("Contact Number"), 4, True, gtk.CellRendererText())
            , TVColumn(COL_ADDRESS, gobject.TYPE_STRING, _("Address"), 5, True, gtk.CellRendererText())
            , TVColumn(COL_CITY, gobject.TYPE_STRING, _("City/Town"), 6, True, gtk.CellRendererText())
            , TVColumn(COL_PROV, gobject.TYPE_STRING, _("State/Province"), 7, True, gtk.CellRendererText())
            , TVColumn(COL_ZIP, gobject.TYPE_STRING, _("Zip Code"), 8, True, gtk.CellRendererText())
            , TVColumn(COL_COUNTRY, gobject.TYPE_STRING, _("Country"), 9, True, gtk.CellRendererText())
        ]
        
        """Called when we want to initialize the tree.
        """
        tree_type_list = [] #For creating the TreeStore
        self.__cu_column_dict = {} #For easy access later on

        #Get the treeView from the widget Tree
        self.reCuTreeview = self.wTree.get_widget("reCuTreeview")
        #Make it so that the colours of each row can alternate
        self.reCuTreeview.set_rules_hint(True)

        # Loop through the columns and initialize the Tree
        for item_column in self.reCuListstore_columns:
            #Add the column to the column dict
            self.__cu_column_dict[item_column.ID] = item_column
            #Save the type for gtk.TreeStore creation
            tree_type_list.append(item_column.type)
            #is it visible?
            if (item_column.visible):
                #Create the Column
                column = gtk.TreeViewColumn(item_column.name
                    , item_column.cellrenderer
                    , text=item_column.pos)
                
                column.set_resizable(True)
                column.set_sort_column_id(item_column.pos)
                self.reCuTreeview.append_column(column)
                
        #Create the gtk.TreeStore Model to use with the inTreeview
        self.reCuListstore = gtk.ListStore(*tree_type_list)
        #Attache the model to the treeView
        self.reCuTreeview.set_model(self.reCuListstore)
        
    def create_reInListstore(self):
        
        self.reInListstore_columns = [
            TVColumn(COL_OBJECT, gobject.TYPE_PYOBJECT, "object", 0)
            , TVColumn(COL_OBJECT_TYPE, gobject.TYPE_INT, "object_type", 1)
            , TVColumn(COL_CODE, gobject.TYPE_STRING, _("Code"), 2, True, gtk.CellRendererText())
            , TVColumn(COL_TITLE, gobject.TYPE_STRING, _("Title"), 3, True, gtk.CellRendererText())
            , TVColumn(COL_GENRES, gobject.TYPE_STRING, _("Days"), 4, True, gtk.CellRendererText())
            , TVColumn(COL_TYPE, gobject.TYPE_STRING, _("Price"), 5, True, gtk.CellRendererText())
        ]
        
        """Called when we want to initialize the tree.
        """
        tree_type_list = [] #For creating the TreeStore
        self.__cu_column_dict = {} #For easy access later on

        #Get the treeView from the widget Tree
        self.reInTreeview = self.wTree.get_widget("reInTreeview")
        #Make it so that the colours of each row can alternate
        self.reInTreeview.set_rules_hint(True)

        # Loop through the columns and initialize the Tree
        for item_column in self.reInListstore_columns:
            #Add the column to the column dict
            self.__cu_column_dict[item_column.ID] = item_column
            #Save the type for gtk.TreeStore creation
            tree_type_list.append(item_column.type)
            #is it visible?
            if (item_column.visible):
                
                #Create the Column
                column = gtk.TreeViewColumn(item_column.name
                    , item_column.cellrenderer
                    , text=item_column.pos)
                
                if item_column.name == _("Price") or item_column.name == _("Days"):
                    
                    item_column.cellrenderer.set_property('xalign', 1)
                    column.set_alignment(1)
                    
                # Set the column to expand if it is the column Title
                column.set_expand(item_column.name == _("Title"))
                    
                column.set_resizable(True)
                column.set_sort_column_id(item_column.pos)
                self.reInTreeview.append_column(column)
                
        #Create the gtk.TreeStore Model to use with the inTreeview
        self.reInListstore = gtk.ListStore(*tree_type_list)
        #Attache the model to the treeView
        self.reInTreeview.set_model(self.reInListstore)
        
    def create_aboutDialog(self):
        
        #load the dialog from the glade file
        wTree = gtk.glade.XML(self.gladefile, "aboutDialog") 
        
        #Get the actual dialog widget
        self.aboutDialog = wTree.get_widget("aboutDialog")
        #self.aboutDialog.set_icon()
        
        if DEBUG:
            
            print _("   Creating aboutDialog........ Done")
            
    def create_inAddEditDialog(self):
        
        # create some controls
        self.create_inListstore()
        self.create_inGenreCombobox()
        
        wTree = gtk.glade.XML(self.gladefile, "inAddEditDialog")
        self.inAddEditDialog = wTree.get_widget("inAddEditDialog")
        self.inAddEditTable = wTree.get_widget("inAddEditTable")
        self.inGenresTreeview = wTree.get_widget("inGenresTreeview")
        self.inCastsTreeview = wTree.get_widget("inCastsTreeview")
        self.inWritersTreeview = wTree.get_widget("inWritersTreeview")
        
        self.inAddEditNotebook = wTree.get_widget("inAddEditNotebook")
        
        self.inReleaseCalendar = CalendarEntry('')
        self.inAddEditTable.attach(self.inReleaseCalendar, 1, 2 , 2, 3)
        self.inReleaseCalendar.show_all()
        
        self.inTitleEntry = wTree.get_widget("inTitleEntry")
        self.inImdbCodeEntry = wTree.get_widget("inImdbCodeEntry")
        self.inDirectorEntry = wTree.get_widget("inDirectorEntry")
        self.inRatingSpin = wTree.get_widget("inRatingSpin")
        self.inPlotEntry = wTree.get_widget("inPlotEntry")
        self.inGenresEntry = wTree.get_widget("inGenresEntry")
        self.inCastsEntry = wTree.get_widget("inCastsEntry")
        self.inWritersEntry = wTree.get_widget("inWritersEntry")
        self.inRentalCostSpin = wTree.get_widget("inRentalCostSpin")
        self.inAllottedDaysSpin = wTree.get_widget("inAllottedDaysSpin")
        self.inStatusCombobox = wTree.get_widget("inStatusCombobox")
        
        self.inGenresAddButton = wTree.get_widget("inGenresAddButton")
        self.inGenresRemoveButton = wTree.get_widget("inGenresRemoveButton")
        self.inCastsAddButton = wTree.get_widget("inCastsAddButton")
        self.inCastsRemoveButton = wTree.get_widget("inCastsRemoveButton")
        self.inWritersAddButton = wTree.get_widget("inWritersAddButton")
        self.inWritersRemoveButton = wTree.get_widget("inWritersRemoveButton")
        
        self.inRevenueLastMonth = wTree.get_widget("inRevenueLastMonth")
        self.inRevenueThisMonth = wTree.get_widget("inRevenueThisMonth")
        self.inRevenueTotal     = wTree.get_widget("inRevenueTotal")
        self.inRentalLastMonth  = wTree.get_widget("inRentalLastMonth")
        self.inRentalThisMonth  = wTree.get_widget("inRentalThisMonth")
        self.inRentalTotal      = wTree.get_widget("inRentalTotal")
        
        self.inDirectorCompletion = gtk.EntryCompletion()
        self.inGenresCompletion = gtk.EntryCompletion()
        self.inCastsCompletion = gtk.EntryCompletion()
        self.inWritersCompletion = gtk.EntryCompletion()
        
        self.inDirectorListstore = gtk.ListStore(str)
        self.inGenresListstore = gtk.ListStore(str)
        self.inCastsListstore = gtk.ListStore(str)
        self.inWritersListstore = gtk.ListStore(str)
        
        for instance in session.query(Director).order_by(Director.full_name):
            
            self.inDirectorListstore.append([instance.full_name])
            
        for instance in session.query(Genre).order_by(Genre.name):
            
            self.inGenresListstore.append([instance.name])
            
        for instance in session.query(Cast).order_by(Cast.full_name):
            
            self.inCastsListstore.append([instance.full_name])
            
        for instance in session.query(Writer).order_by(Writer.full_name):
            
            self.inWritersListstore.append([instance.full_name])
            
        self.inDirectorCompletion.set_model(self.inDirectorListstore)
        self.inGenresCompletion.set_model(self.inGenresListstore)
        self.inCastsCompletion.set_model(self.inCastsListstore)
        self.inWritersCompletion.set_model(self.inWritersListstore)
        
        self.inDirectorEntry.set_completion(self.inDirectorCompletion)
        self.inGenresEntry.set_completion(self.inGenresCompletion)
        self.inCastsEntry.set_completion(self.inCastsCompletion)
        self.inWritersEntry.set_completion(self.inWritersCompletion)
        
        self.inDirectorCompletion.set_text_column(0)
        self.inGenresCompletion.set_text_column(0)
        self.inCastsCompletion.set_text_column(0)
        self.inWritersCompletion.set_text_column(0)
        
        self.inTitleLabel        = wTree.get_widget("inTitleLabel")
        self.inImdbCodeLabel     = wTree.get_widget("inImdbCodeLabel")
        self.inReleaseLabel      = wTree.get_widget("inReleaseLabel")
        self.inDirectorLabel     = wTree.get_widget("inDirectorLabel")
        self.inRatingLabel       = wTree.get_widget("inRatingLabel")
        self.inPlotLabel         = wTree.get_widget("inPlotLabel")
        self.inGenresLabel       = wTree.get_widget("inGenresLabel")
        self.inCastsLabel        = wTree.get_widget("inCastsLabel")
        self.inWritersLabel      = wTree.get_widget("inWritersLabel")
        self.inRentalCostLabel   = wTree.get_widget("inRentalCostLabel")
        self.inAllottedDaysLabel = wTree.get_widget("inAllottedDaysLabel")
        self.inStatusLabel       = wTree.get_widget("inStatusLabel")
        
        self.inReleaseLabel.set_mnemonic_widget(self.inReleaseCalendar.entry)
        
        self.create_inGenreListstore()
        self.create_inCastListstore()
        self.create_inWriterListstore()
        
        self.inStatusListstore = gtk.ListStore(str)
        cellRenderer = gtk.CellRendererText()
        
        status = (_('Select one'), _('Available'), _('Rented'), _('Out of order'))
        
        for s in status:
            
            self.inStatusListstore.append([s])
            
        self.inStatusCombobox.pack_start(cellRenderer, True)
        self.inStatusCombobox.add_attribute(cellRenderer, 'text', 0)
        self.inStatusCombobox.set_model(self.inStatusListstore)
        self.inStatusCombobox.set_active(0)
        
        self.inWidgets = \
            [
                [self.inTitleEntry, self.inTitleLabel, _("_Title:"), 0],
                [self.inImdbCodeEntry, self.inImdbCodeLabel, _("_IMDB Code:"), 0],
                [self.inReleaseCalendar.entry, self.inReleaseLabel, _("_Release:"), 0],
                [self.inDirectorEntry, self.inDirectorLabel, _("_Director:"), 0],
                [self.inRatingSpin, self.inRatingLabel, _("Rati_ng:"), 0],
                [self.inPlotEntry, self.inPlotLabel, _("_Plot:"), 0],
                [self.inGenresTreeview, self.inGenresLabel, _("G_enres:"), 0],
                [self.inCastsTreeview, self.inCastsLabel, _("Cas_ts:"), 1],
                [self.inWritersTreeview, self.inWritersLabel, _("_Writers:"), 1],
                [self.inRentalCostSpin, self.inRentalCostLabel, _("_Rental Cost:"), 2],
                [self.inAllottedDaysSpin, self.inAllottedDaysLabel, _("All_otted Days:"), 2],
                [self.inStatusCombobox, self.inStatusLabel, _("Stat_us:"), 2],
            ]
        
        if DEBUG:
            
            print _("   Creating inAddEditDialog.... Done")
            
        wTree.signal_autoconnect(self)
        
    def create_cuAddEditDialog(self):
        
        wTree = gtk.glade.XML(self.gladefile, "cuAddEditDialog")
        
        self.cuAddEditDialog      = wTree.get_widget("cuAddEditDialog")
        
        self.cuPrefixLabel        = wTree.get_widget("cuPrefixLabel")
        self.cuLastnameEntry      = wTree.get_widget("cuLastnameEntry")
        self.cuFirstnameEntry     = wTree.get_widget("cuFirstnameEntry")
        self.cuMiddlenameEntry    = wTree.get_widget("cuMiddlenameEntry")
        self.cuContactnumberEntry = wTree.get_widget("cuContactnumberEntry")
        self.cuZipcodeEntry       = wTree.get_widget("cuZipcodeEntry")
        self.cuStreetEntry        = wTree.get_widget("cuStreetEntry")
        self.cuGenderCombobox     = wTree.get_widget("cuGenderCombobox")
        self.cuCityCombobox       = wTree.get_widget("cuCityCombobox")
        self.cuStateCombobox      = wTree.get_widget("cuStateCombobox")
        self.cuCountryCombobox    = wTree.get_widget("cuCountryCombobox")
        
        self.cuLastnameLabel      = wTree.get_widget("cuLastnameLabel")
        self.cuFirstnameLabel     = wTree.get_widget("cuFirstnameLabel")
        self.cuMiddlenameLabel    = wTree.get_widget("cuMiddlenameLabel")
        self.cuContactnumberLabel = wTree.get_widget("cuContactnumberLabel")
        self.cuGenderLabel        = wTree.get_widget("cuGenderLabel")
        self.cuStreetLabel        = wTree.get_widget("cuStreetLabel")
        self.cuCityLabel          = wTree.get_widget("cuCityLabel")
        self.cuZipcodeLabel       = wTree.get_widget("cuZipcodeLabel")
        self.cuStateLabel         = wTree.get_widget("cuStateLabel")
        self.cuCountryLabel       = wTree.get_widget("cuCountryLabel")
        
        self.cuContactnumberHbox  = wTree.get_widget("cuContactnumberHbox")
        
        # create some controls
        self.create_cuListstore()
        self.create_cuComboboxes()
        
        self.cuWidgets = \
        [
            [self.cuLastnameEntry, self.cuLastnameLabel, _("_Last Name:")], 
            [self.cuFirstnameEntry, self.cuFirstnameLabel, _("_First Name:")], 
            [self.cuMiddlenameEntry, self.cuMiddlenameLabel, _("_Middle Name:")], 
            [self.cuGenderCombobox, self.cuGenderLabel, _("_Gender:")], 
            [self.cuContactnumberEntry, self.cuContactnumberLabel, _("C_ontact Number:")], 
            [self.cuStreetEntry, self.cuStreetLabel, _("St_reet:")], 
            [self.cuCityCombobox, self.cuCityLabel, _("C_ity/Town:")], 
            [self.cuZipcodeEntry, self.cuZipcodeLabel, _("_Zip Code:")], 
            [self.cuStateCombobox, self.cuStateLabel, _("S_tate/Province:")], 
            [self.cuCountryCombobox, self.cuCountryLabel, _("Co_untry:")], 
        ]
        
        size_group = gtk.SizeGroup(gtk.SIZE_GROUP_HORIZONTAL)
        for widget in self.cuWidgets:
            
            if widget[2] != _("C_ontact Number:"):
                
                size_group.add_widget(widget[0])
                
            else:
                
                size_group.add_widget(self.cuContactnumberHbox)
        
        self.cuPrefixLabel.set_label(PREFIX)
        
        self.cuLastnameEntry.set_activates_default(True)
        self.cuFirstnameEntry.set_activates_default(True)
        self.cuMiddlenameEntry.set_activates_default(True)
        self.cuContactnumberEntry.set_activates_default(True)
        self.cuStreetEntry.set_activates_default(True)
        self.cuZipcodeEntry.set_activates_default(True)
        
        if DEBUG:
            
            print _("   Creating cuAddEditDialog.... Done")
            
        wTree.signal_autoconnect(self)
            
    def create_inGenreCombobox(self):
        
        self.inGenreCombobox = self.wTree.get_widget("inGenreCombobox")
        
        self.inGenreListStore = gtk.ListStore(str)
        cellRenderer = gtk.CellRendererText()
        
        self.inGenreCombobox.pack_start(cellRenderer, True)
        self.inGenreCombobox.add_attribute(cellRenderer, 'text', 0)
        
        self.inGenreListStore.append([_('All Genres')])
        
        for genre in session.query(Genre).order_by(Genre.name):
            
            self.inGenreListStore.append([genre.name])
            
        self.inGenreCombobox.set_model(self.inGenreListStore)
        self.inGenreCombobox.set_active(0)
        
    def create_cuComboboxes(self):
        
        self.cuGenderListStore = gtk.ListStore(str)
        self.cuCityListStore = gtk.ListStore(str)
        self.cuStateListStore = gtk.ListStore(str)
        self.cuCountryListStore = gtk.ListStore(str)
        cellRenderer = gtk.CellRendererText()
        
        self.cuGenderCombobox.pack_start(cellRenderer, True)
        self.cuGenderCombobox.add_attribute(cellRenderer, 'text', 0)
        self.cuCityCombobox.pack_start(cellRenderer, True)
        self.cuCityCombobox.add_attribute(cellRenderer, 'text', 0)
        self.cuStateCombobox.pack_start(cellRenderer, True)
        self.cuStateCombobox.add_attribute(cellRenderer, 'text', 0)
        self.cuCountryCombobox.pack_start(cellRenderer, True)
        self.cuCountryCombobox.add_attribute(cellRenderer, 'text', 0)
        
        # Gender
        li = [_('Select one'), _('Male'), _('Female')]
        for item in li:
            
            self.cuGenderListStore.append([item])
            
        # City
        self.cuCityListStore.append([_('Select one')])
        for city in session.query(City):
            
            self.cuCityListStore.append([city.name])
            
        # State
        self.cuStateListStore.append([_('Select one')])
        for state in session.query(State).order_by(State.name):
            
            self.cuStateListStore.append([state.name])
            
        # Country
        self.cuCountryListStore.append([_('Select one')])
        for country in session.query(Country).order_by(Country.name):
            
            self.cuCountryListStore.append([country.name])
            
        self.cuGenderCombobox.set_model(self.cuGenderListStore)
        self.cuGenderCombobox.set_active(0)
        self.cuCityCombobox.set_model(self.cuCityListStore)
        self.cuCityCombobox.set_active(0)
        self.cuStateCombobox.set_model(self.cuStateListStore)
        self.cuStateCombobox.set_active(0)
        self.cuCountryCombobox.set_model(self.cuCountryListStore)
        self.cuCountryCombobox.set_active(0)
        
    #***************************************************************************
    # Signal Handlers
    #***************************************************************************
    def on_mainWindow_destroy(self, widget):
        """Called when the application is going to quit"""
        
        gtk.main_quit()

    def on_aboutDialog_activate(self, widget):
        
        self.aboutDialog.run()
        
        #we are done with the dialog, hide it
        self.aboutDialog.hide()
        
    def on_inEntries_focus_in_event(self, widget, event):
        
        self.inGenresRemoveButton.set_sensitive(False)
        self.inCastsRemoveButton.set_sensitive(False)
        self.inWritersRemoveButton.set_sensitive(False)
        
        self.inGenresTreeview.get_selection().unselect_all()
        self.inCastsTreeview.get_selection().unselect_all()
        self.inWritersTreeview.get_selection().unselect_all()
        
    def on_inAddButton_clicked(self, widget):
        
        self.inAddEditDialog.set_title(_("Add Movie Dialog"))
        self.inTitleEntry.grab_focus()
        
        self.inRevenueLastMonth.set_text('0.00')
        self.inRevenueThisMonth.set_text('0.00')
        self.inRevenueTotal.set_text('0.00')
        
        self.inRentalLastMonth.set_text('-')
        self.inRentalThisMonth.set_text('-')
        self.inRentalTotal.set_text('-')
        
        result = self.inAddEditDialog.run()
        
        while result == gtk.RESPONSE_OK and \
              self.validate_widgets(self.inWidgets, self.inAddEditNotebook) == -1:
            
            result = self.inAddEditDialog.run()
            
            self.reset_widgets(self.inWidgets, False, self.inAddEditNotebook)
            
        self.inAddEditDialog.hide()
        
        if result == gtk.RESPONSE_OK:
            
            self.inPerformAdd()
        
        self.reset_widgets(self.inWidgets, notebook=self.inAddEditNotebook)
        
    def on_inGenresTreeview_cursor_changed(self, widget):
        
        self.inGenresRemoveButton.set_sensitive(True)
        
    def on_inCastsTreeview_cursor_changed(self, widget):
        
        self.inCastsRemoveButton.set_sensitive(True)
        
    def on_inWritersTreeview_cursor_changed(self, widget):
        
        self.inWritersRemoveButton.set_sensitive(True)
        
    def on_inGenresAddButton_clicked(self, widget):
        
        genre = []
        in_liststore = False
        
        try:
            
            g = session.query(Genre).filter(self.inGenresEntry.get_text()==Genre.name).one()
            
            genre.extend([g, g.id, g.name])
            
        except NoResultFound:
            
            return
        
        _iter = self.inGenresAddEditListstore.get_iter_first()
        
        while _iter is not None:
            
            value = self.inGenresAddEditListstore.get_value(_iter, 2)
            
            if value == g.name:
                
                in_liststore = True
                
            _iter = self.inGenresAddEditListstore.iter_next(_iter)
            
        if not in_liststore:
            
            self.inGenresAddEditListstore.append(genre)
            
        self.inGenresEntry.set_text("")
        self.inGenresEntry.grab_focus()
        
    def on_inCastsAddButton_clicked(self, widget):
        
        cast = []
        in_liststore = False
        
        try:
            
            c = session.query(Cast).filter(self.inCastsEntry.get_text()==Cast.full_name).one()
            
            cast.extend([c, c.id, c.full_name])
            
        except NoResultFound:
            
            if self.inCastsEntry.get_text() != "":
                
                c = Cast(self.inCastsEntry.get_text())
                
                cast.extend([c, -1, c.full_name])
                
                self.inCastsListstore.append([c.full_name])
                
            else:
                
                return
            
        _iter = self.inCastsAddEditListstore.get_iter_first()
        
        while _iter is not None:
            
            value = self.inCastsAddEditListstore.get_value(_iter, 2)
            
            if value == c.full_name:
                
                in_liststore = True
                
            _iter = self.inCastsAddEditListstore.iter_next(_iter)
            
        if not in_liststore:
            
            self.inCastsAddEditListstore.append(cast)
            
        self.inCastsEntry.set_text("")
        self.inCastsEntry.grab_focus()
        
    def on_inWritersAddButton_clicked(self, widget):
        
        writer = []
        in_liststore = False
        
        try:
            
            w = session.query(Writer).filter(self.inWritersEntry.get_text()==Writer.full_name).one()
            
            writer.extend([w, w.id, w.full_name])
            
        except NoResultFound:
            
            if self.inWritersEntry.get_text() != "":
                
                w = Writer(self.inWritersEntry.get_text())
                
                writer.extend([w, -1, w.full_name])
                
                self.inWritersListstore.append([w.full_name])
                
            else:
                
                return
            
        _iter = self.inWritersAddEditListstore.get_iter_first()
        
        while _iter is not None:
            
            value = self.inWritersAddEditListstore.get_value(_iter, 2)
            
            if value == w.full_name:
                
                in_liststore = True
                
            _iter = self.inWritersAddEditListstore.iter_next(_iter)
            
        if not in_liststore:
            
            self.inWritersAddEditListstore.append(writer)
            
        self.inWritersEntry.set_text("")
        self.inWritersEntry.grab_focus()
        
    def on_inGenresRemoveButton_clicked(self, widget):
        
        selected_row = self.inGenresTreeview.get_selection().get_selected_rows()
        
        _iter = self.inGenresAddEditListstore.get_iter(selected_row[1][0])
        self.inGenresAddEditListstore.remove(_iter)
        
        self.inGenresTreeview.get_selection().unselect_all()
        self.inGenresRemoveButton.set_sensitive(False)
        
        print 'on_inGenresRemoveButton_clicked'
        
    def on_inCastsRemoveButton_clicked(self, widget):
        
        selected_row = self.inCastsTreeview.get_selection().get_selected_rows()
        
        _iter = self.inCastsAddEditListstore.get_iter(selected_row[1][0])
        self.inCastsAddEditListstore.remove(_iter)
        
        self.inCastsTreeview.get_selection().unselect_all()
        self.inCastsRemoveButton.set_sensitive(False)
        
    def on_inWritersRemoveButton_clicked(self, widget):
        
        selected_row = self.inWritersTreeview.get_selection().get_selected_rows()
        
        _iter = self.inWritersAddEditListstore.get_iter(selected_row[1][0])
        self.inWritersAddEditListstore.remove(_iter)
        
        self.inWritersTreeview.get_selection().unselect_all()
        self.inWritersRemoveButton.set_sensitive(False)
        
    def on_inGenresEntry_key_press_event(self, widget, event):
        
        if event.hardware_keycode == 13:
            
            self.on_inGenresAddButton_clicked(widget)
            
    def on_inCastsEntry_key_press_event(self, widget, event):
        
        if event.hardware_keycode == 13:
            
            self.on_inCastsAddButton_clicked(widget)
            
    def on_inWritersEntry_key_press_event(self, widget, event):
        
        if event.hardware_keycode == 13:
            
            self.on_inWritersAddButton_clicked(widget)
            
    def on_cuAddButton_clicked(self, widget):
        
        self.cuLastnameEntry.grab_focus()
        
        self.cuAddEditDialog.set_title(_("Add Customer Dialog"))
        
        result = self.cuAddEditDialog.run()
        
        while result == gtk.RESPONSE_OK and self.validate_widgets(self.cuWidgets) == -1:
            
            result = self.cuAddEditDialog.run()
            
            self.reset_widgets(self.cuWidgets, False)
            
        self.cuAddEditDialog.hide()
        
        if result == gtk.RESPONSE_OK:
            
            self.cuPerformAdd()
            
        self.reset_widgets(self.cuWidgets)
        
    def on_inTreeview_row_activated(self, treeview, path, column):
        
        #status = {1:_("Available"), 2:_("Rented"), 3:_("Out of order")}
        
        self.inAddEditDialog.set_title(_("Edit Movie Dialog"))
        
        inModel = treeview.get_model()
        inIter  = inModel.get_iter(path)
        
        m = inModel.get_value(inIter, 0)
        
        self.inTitleEntry.set_text(m.title)
        self.inImdbCodeEntry.set_text(m.imdbCode)
        
        rDate = m.release.split('-')
        self.inReleaseCalendar.set_date(datetime.date(int(rDate[0]), int(rDate[1]), int(rDate[2])))
        self.inReleaseCalendar.update_entry()
        
        self.inDirectorEntry.set_text(m.director.full_name)
        self.inRatingSpin.set_value(float(m.rating))
        self.inPlotEntry.set_text(m.plot)
        self.inRentalCostSpin.set_value(float(m.rent))
        self.inAllottedDaysSpin.set_value(float(m.allotted))
        self.inStatusCombobox.set_active(m.status)
        
        if m.status == 2:
            
            self.inStatusCombobox.set_sensitive(False)
        
        revenue = m.revenue.split('|')
        self.inRevenueLastMonth.set_text(revenue[0])
        self.inRevenueThisMonth.set_text(revenue[1])
        self.inRevenueTotal.set_text(revenue[2])
        
        rental = m.rental.split('|')
        self.inRentalLastMonth.set_text(rental[0])
        self.inRentalThisMonth.set_text(rental[1])
        self.inRentalTotal.set_text(rental[2])
        
        for genre in m.genres:
            
            self.inGenresAddEditListstore.append([genre, genre.id, genre.name])
            
        for cast in m.casts:
            
            self.inCastsAddEditListstore.append([cast, cast.id, cast.full_name])
            
        for writer in m.writers:
            
            self.inWritersAddEditListstore.append([writer, writer.id, writer.full_name])
        
        self.inTitleEntry.grab_focus()
        
        result = self.inAddEditDialog.run()
        
        while result == gtk.RESPONSE_OK and \
              self.validate_widgets(self.inWidgets, self.inAddEditNotebook) == -1:
            
            result = self.inAddEditDialog.run()
            
            self.reset_widgets(self.inWidgets, False, self.inAddEditNotebook)
            
        self.inAddEditDialog.hide()
        
        if result == gtk.RESPONSE_OK:
            
            m = self.inPerformEdit(m)
            
            self.inListstore.set(inIter, 
                COL_OBJECT, m, 
                COL_OBJECT_TYPE, m.id,
                COL_CODE, m.id,
                COL_NAME, "%s (%s)" % (m.title, m.release[0:4]),
                COL_GENRES, list2str(m.genres),
                COL_TYPE, m.director.full_name)
        
        self.reset_widgets(self.inWidgets, notebook=self.inAddEditNotebook)
        
    def on_inTreeview_key_press_event(self, widget, event):
        
        if event.hardware_keycode == 46:
            
            model = widget.get_model()
            selected = widget.get_selection().get_selected()
            
            row = selected[0][selected[1]]
            
            instance = row[0]
            
            model.remove(selected[1])
            
            ## Show warning dialog here
            
            session.delete(instance)
            session.commit()
            #print session.query(Movie).filter(Movie.title==instance.title).count()
            print session.query(Cast).filter(Cast.full_name=="Daniel Craig").count()
        
        pass
        
    def on_cuTreeview_row_activated(self, treeview, path, column):
        
        self.cuAddEditDialog.set_title(_("Edit Customer Dialog"))
        
        cuModel = treeview.get_model()
        cuIter  = cuModel.get_iter(path)
        
        cust = cuModel.get_value(cuIter, 0)
        
        self.cuLastnameEntry.set_text(cust.last_name)
        self.cuFirstnameEntry.set_text(cust.first_name)
        self.cuMiddlenameEntry.set_text(cust.middle_name)
        self.cuContactnumberEntry.set_text(cust.contact_number[3:])
        self.cuZipcodeEntry.set_text(cust.zip_code)
        self.cuStreetEntry.set_text(cust.street)
        
        self.cuGenderCombobox.set_active(cust.gender)
        
        ciIter = self.cuCityCombobox.get_active_iter()
        ciModel = self.cuCityCombobox.get_model()
        saIter = self.cuStateCombobox.get_active_iter()
        saModel = self.cuStateCombobox.get_model()
        coIter = self.cuCountryCombobox.get_active_iter()
        coModel = self.cuCountryCombobox.get_model()
        
        while ciIter is not None:
            
            if ciModel[ciIter][0] != cust.city.name:
                
                ciIter = ciModel.iter_next(ciIter)
                
            else:
                
                self.cuCityCombobox.set_active_iter(ciIter)
                
                break
            
        while saIter is not None:
            
            if saModel[saIter][0] != cust.state.name:
                
                saIter = saModel.iter_next(saIter)
                
            else:
                
                self.cuStateCombobox.set_active_iter(saIter)
                
                break
            
        while coIter is not None:
            
            if coModel[coIter][0] != cust.country.name:
                
                coIter = coModel.iter_next(coIter)
                
            else:
                
                self.cuCountryCombobox.set_active_iter(coIter)
                
                break
        
        self.cuLastnameEntry.grab_focus()
        
        result = self.cuAddEditDialog.run()
        
        while result == gtk.RESPONSE_OK and self.validate_widgets(self.cuWidgets) == -1:
            
            result = self.cuAddEditDialog.run()
            
        
        self.cuAddEditDialog.hide()
        
        if result == gtk.RESPONSE_OK:
            
            gender = {1:_("(M)"), 2:_("(F)")}
            
            cust = self.cuPerformEdit(cust)
            
            self.cuListstore.set(cuIter, 
                COL_OBJECT, cust, 
                COL_OBJECT_TYPE, cust.id,
                COL_NAME, "%s %s" % (cust.full_name, gender[cust.gender]),
                COL_ADDRESS, cust.street,
                COL_CITY, cust.city.name,
                COL_ZIP, cust.zip_code,
                COL_PROV, cust.state.name,
                COL_COUNTRY, cust.country.name)
        
        self.reset_widgets(self.cuWidgets)
        
    def on_reCuTreeview_row_activated(self, treeview, path, column):
        
        reCuModel = treeview.get_model()
        reCuIter = reCuModel.get_iter(path)
        
        customer = reCuModel.get_value(reCuIter, 0)
        
        self.rePerformRental(customer)
        
    def on_reCuEntry_key_press_event(self, widget, event):
        
        self.reCuCode = self.wTree.get_widget("reCuCode")
        self.reCuName = self.wTree.get_widget("reCuName")
        self.reCuAddress = self.wTree.get_widget("reCuAddress")
        self.reCuAddress2 = self.wTree.get_widget("reCuAddress2")
        self.reCuCity = self.wTree.get_widget("reCuCity")
        self.reCuState = self.wTree.get_widget("reCuState")
        
        if event.hardware_keycode == 13:
            
            string = self.reCuEntry.get_text()
            self.reCuListstore.clear()
            
            try:
                
                customer = session.query(Customer).filter(Customer.id==string).one()
                
            except NoResultFound:
                
                regex = re.compile('%s' % string, re.IGNORECASE)
                
                customerList = []
                for customer in session.query(Customer):
                    
                    if (regex.search(customer.first_name) or regex.search(customer.last_name) \
                       or regex.search(customer.middle_name) or regex.search(customer.street) \
                       or regex.search(str(customer.id))) and customer not in customerList:
                        
                        customerList += [customer]
                        
                self.update_reCuListstore(customerList)
                self.reCuTreeview.set_headers_visible(True)
                
                return
                
            self.rePerformRental(customer)
            
    def on_reInEntry_key_press_event(self, widget, event):
        
        if event.hardware_keycode == 13:
            
            string = self.reInEntry.get_text()
            self.reInEntry.set_text("")
            
            try:
                
                movie = session.query(Movie).filter(Movie.id==string).one()
                
            except NoResultFound:
                
                self.reInAlertLabel.set_label("<span foreground='red'>Movie code %s isn't in the database.</span>" % string)
                return
            
            if not self.in_movie_list(movie, self.reInListstore):
                
                self.update_reInListstore([movie])
                
            self.reInTreeview.set_headers_visible(True)
    def on_inShowAllButton_clicked(self, widget):
        
        self.inEntry.set_text("")
        self.inGenreCombobox.set_active(0)
        self.inListstore.clear()
        self.inEntry.grab_focus()
        
        movieList = []
        for genre in session.query(Genre):
            
            for movie in genre.movies:
                
                if movie not in movieList:
                    
                    movieList += [movie]
            
        self.update_inListstore(movieList)
        
    def on_cuShowAllButton_clicked(self, widget):
        
        self.cuEntry.set_text("")
        self.cuListstore.clear()
        self.cuEntry.grab_focus()
        
        customerList = []
        for customer in session.query(Customer):
                
            if customer not in customerList:
                    
                customerList += [customer]
            
        self.update_cuListstore(customerList)
        
    def on_inFindButton_clicked(self, widget):
        
        self.set_cursor("watch")
        
        genreModel = self.inGenreCombobox.get_model()
        genreActive = self.inGenreCombobox.get_active()
        
        searchTitle  = self.inEntry.get_text()
        searchFilter = genreModel[genreActive][0]
        
        self.inListstore.clear()
        self.inEntry.grab_focus()
        
        if searchFilter == _("All Genres") and searchTitle == "":
            
            self.on_inShowAllButton_clicked(widget)
            
            return
        else:
            
            regex = re.compile('%s' % searchTitle, re.IGNORECASE)
            
        movieList = []
        if searchFilter != _('All Genres'):
            
            query = session.query(Genre).filter(Genre.name==searchFilter).\
                  order_by(Genre.name)
            
        else:
            
            query = session.query(Genre).order_by(Genre.name)
            
        for genre in query:
            
            for movie in genre.movies:
                
                movieList = self.get_moviesByCast(regex, movie, movieList)
                
                if (regex.search(movie.title) or regex.search(movie.release[0:4]) or \
                   regex.search(str(movie.id)) or regex.search(movie.director.full_name)) \
                   and movie not in movieList:
                    
                    movieList += [movie]
                    
        self.update_inListstore(movieList)
        
        self.root_window.set_cursor(None)
        
    def on_cuFindButton_clicked(self, widget):
        
        self.set_cursor("watch")
        
        searchTitle = self.cuEntry.get_text()
        
        self.cuListstore.clear()
        self.cuEntry.grab_focus()
        
        if searchTitle == "":
            
            self.on_cuShowAllButton_clicked(widget)
            
            return
        
        else:
            
            regex = re.compile('%s' % searchTitle, re.IGNORECASE)
            
        customerList = []
        for customer in session.query(Customer):
            
            if (regex.search(customer.first_name) or regex.search(customer.last_name) \
               or regex.search(customer.middle_name) or regex.search(customer.street) \
               or regex.search(str(customer.id))) and customer not in customerList:
                
                customerList += [customer]
                
        self.update_cuListstore(customerList)
        
        self.root_window.set_cursor(None)
    def on_reButton_clicked(self, widget):
        
        # clear the liststore
        self.reCuListstore.clear()
        self.reInListstore.clear()
        
        self.reCuEntry.grab_focus()
        
        # set some attributes
        self.notebook.set_current_page(0)
        self.reNotebook.set_current_page(0)
        self.reCuEntry.set_text("")
        self.reInEntry.set_text("")
        self.reInAlertLabel.set_label("")
        self.reCuTreeview.set_headers_visible(False)
        
    def on_inButton_clicked(self, widget):
        
        self.notebook.set_current_page(1)
        self.reNotebook.set_current_page(0)
        
        self.inEntry = self.wTree.get_widget("inEntry")
        self.inFindButton = self.wTree.get_widget("inFindButton")
        
        self.inEntry.set_activates_default(True)
        self.inEntry.grab_focus()
        
        self.inFindButton.grab_default()
        
    def on_cuButton_clicked(self, widget):
        
        self.notebook.set_current_page(2)
        self.reNotebook.set_current_page(0)
        
        self.cuEntry = self.wTree.get_widget("cuEntry")
        self.cuFindButton = self.wTree.get_widget("cuFindButton")
        
        self.cuEntry.set_activates_default(True)
        self.cuEntry.grab_focus()
        
        self.cuFindButton.grab_default()
        
    def on_trButton_clicked(self, widget):
        
        self.notebook.set_current_page(3)
        self.reNotebook.set_current_page(0)
        
    def on_rpButton_clicked(self, widget):
        
        self.notebook.set_current_page(4)
        self.reNotebook.set_current_page(0)
        
    def on_maButton_clicked(self, widget):
        
        self.notebook.set_current_page(5)
        self.reNotebook.set_current_page(0)
        
    def on_daButton_clicked(self, widget):
        
        self.notebook.set_current_page(6)
        self.reNotebook.set_current_page(0)
        
    def on_menuButton_clicked(self, widget):
        
        label = widget.get_label()
        
        buttonDict = {
            _("_Rentals"):0, _("_Inventory"):1, _("_Customers"):2, 
            _("_Transactions"):3, _("Rep_orts"):4, _("_Maintenance"):5, 
            _("_Day-End"):6
        }
        
        self.notebook.set_current_page(buttonDict[label])
        
        if label == _("_Customers"):
            
            self.cuEntry = self.wTree.get_widget("cuEntry")
            self.cuFindButton = self.wTree.get_widget("cuFindButton")
            
            self.cuEntry.set_activates_default(True)
            self.cuEntry.grab_focus()
            
            self.cuFindButton.grab_default()
        
    def reset_widgets(self, widgetsList, value=True, notebook=None):
        
        for w in widgetsList:
            
            widget = w[0]
            label  = w[1]
            text   = w[2]
            
            if notebook:
                
                notebook.set_current_page(0)
            
            label.set_markup_with_mnemonic("%s" % text)
            widget.set_sensitive(True)
            
            if value:
                
                if isinstance(widget, gtk.Entry):
                    
                    widget.set_text("")
                    
                elif isinstance(widget, gtk.ComboBox):
                    
                    widget.set_active(0)
                    
                elif isinstance(widget, gtk.TreeView):
                    
                    model = widget.get_model()
                    model.clear()
                    
                    entries = {
                        "inGenresAddEditListstore"  : self.inGenresEntry,
                        "inCastsAddEditListstore"   : self.inCastsEntry,
                        "inWritersAddEditListstore" : self.inWritersEntry
                    }
                    
                    entry = entries[model.get_name()]
                    
                    if entry:
                        
                        entry.set_text("")
                        
                    widget.get_selection().unselect_all()
                    
                elif isinstance(widget, gtk.SpinButton):
                    
                    widget.set_value(0.0)
                    
    def validate_widgets(self, widgetsList, notebook=None):
        
        """Widget Validator
        Validates all the widgets from the widgetList for possible errors.
        """
        
        types = (gtk.Entry, gtk.ComboBox, gtk.TreeView, gtk.SpinButton)
        
        ret_value = 0
        
        for w in widgetsList:
            
            widget = w[0]
            label  = w[1]
            text   = w[2]
            
            if notebook:
                
                notebook.set_current_page(w[3])
                
            if isinstance(widget, types[0]):
                
                if widget.get_text() == "":
                    
                    label.set_markup_with_mnemonic("<span style='italic' foreground='red'>%s</span>" % text)
                    
                    widget.grab_focus()
                    
                    ret_value = -1
                    
                    break
                
                else:
                    
                    label.set_markup_with_mnemonic("%s" % text)
                    
            elif isinstance(widget, types[1]):
                
                model = widget.get_model()
                active = widget.get_active()
                
                if model[active][0] == _('Select one'):
                    
                    label.set_markup_with_mnemonic("<span style='italic' foreground='red'>%s</span>" % text)
                    
                    widget.grab_focus()
                    
                    ret_value = -1
                    
                    break
                    
                else:
                    
                    label.set_markup_with_mnemonic("%s" % text)
                    
            elif isinstance(widget, types[2]):
                
                entries = {
                    "inGenresAddEditListstore"  : self.inGenresEntry,
                    "inCastsAddEditListstore"   : self.inCastsEntry,
                    "inWritersAddEditListstore" : self.inWritersEntry
                }
                
                model = widget.get_model()
                
                if not model:
                    
                    entry = entries[model.get_name()]
                    
                    if entry:
                        
                        entry.grab_focus()
                        
                    label.set_markup_with_mnemonic("<span style='italic' foreground='red'>%s</span>" % text)
                    
                    ret_value = -1
                    
                    break
                
                else:
                    
                    label.set_markup_with_mnemonic("%s" % text)
                    
            elif isinstance(widget, types[3]):
                
                if widget.get_value() == 0.0:
                    
                    label.set_markup_with_mnemonic("<span style='italic' foreground='red'>%s</span>" % text)
                    
                    widget.grab_focus()
                    
                    ret_value = -1
                    
                    break
                
                else:
                    
                    label.set_markup_with_mnemonic("%s" % text)
                
        return ret_value
    
    def in_movie_list(self, movie, liststore):
        
        """Checks if the movie object is in the liststore."""
        
        _iter = liststore.get_iter_first()
        return_val = False
        
        self.reInAlertLabel.set_label("")
        
        while _iter is not None:
            
            m = liststore.get_value(_iter, 0)
            
            if m != movie:
                
                pass
            
            elif m == movie:
                
                return_val = True
                self.reInAlertLabel.set_label("<span foreground='red'>%s is already in the list.</span>" % m.title)
                
            elif m.status != 2:
                
                return_val = True
                
            elif m.status == 2:
                
                return_val = True
                self.reInAlertLabel.set_label("<span foreground='red'>%s has already been rented.</span>" % m.title)
                
            _iter = liststore.iter_next(_iter)
                
        return return_val
        
    def cuPerformEdit(self, cust):
        
        """
        Performs the actual customer edit. This method updates both GUI 
        and the database.
        """
        
        self.set_cursor("watch")
        
        gender = {_("Male"):1, _("Female"):2}
        
        gnModel = self.cuGenderCombobox.get_model()
        gnActive = self.cuGenderCombobox.get_active()
        ciModel = self.cuCityCombobox.get_model()
        ciActive = self.cuCityCombobox.get_active()
        saModel = self.cuStateCombobox.get_model()
        saActive = self.cuStateCombobox.get_active()
        coModel = self.cuCountryCombobox.get_model()
        coActive = self.cuCountryCombobox.get_active()
        
        cust.last_name = self.cuLastnameEntry.get_text()
        cust.first_name = self.cuFirstnameEntry.get_text()
        cust.middle_name = self.cuMiddlenameEntry.get_text()
        cust.full_name = "%s, %s %s." % \
            (cust.last_name, cust.first_name, cust.middle_name[0])
        cust.street = self.cuStreetEntry.get_text()
        cust.zip_code = self.cuZipcodeEntry.get_text()
        cust.contact_number = PREFIX + self.cuContactnumberEntry.get_text()
        cust.gender = gender[gnModel[gnActive][0]]
        ci = ciModel[ciActive][0]
        sa = saModel[saActive][0]
        co = coModel[coActive][0]
        
        cust = insertCustomer(session, cust, ci, sa, co)
        
        self.root_window.set_cursor(None)
        
        return cust
    
    def inPerformEdit(self, movie):
        
        """
        Performs the actual inventory edit. This method updates both GUI 
        and the database.
        """
        
        self.set_cursor("watch")
        
        movie.title    = self.inTitleEntry.get_text()
        movie.imdbCode = self.inImdbCodeEntry.get_text()
        movie.release  = str(self.inReleaseCalendar.get_date())
        movie.plot     = self.inPlotEntry.get_text()
        movie.rating   = self.inRatingSpin.get_value()
        movie.rent     = self.inRentalCostSpin.get_value()
        movie.allotted = self.inAllottedDaysSpin.get_value()
        movie.status   = self.inStatusCombobox.get_active()
        
        self.inGenresSelectedList = []
        self.inCastsSelectedList = []
        self.inWritersSelectedList = []
        
        try:
            
            director = session.query(Director).filter(Director.full_name==self.inDirectorEntry.get_text()).one()
            
        except NoResultFound:
            
            director = Director(self.inDirectorEntry.get_text())
            
            self.inDirectorListstore.append(director, -1, director.full_name)
            
        # selected genres
        _iter = self.inGenresAddEditListstore.get_iter_first()
        while _iter is not None:
            
            self.inGenresSelectedList.append(self.inGenresAddEditListstore.get_value(_iter, 0))
            
            _iter = self.inGenresAddEditListstore.iter_next(_iter)
            
        # selected casts
        _iter = self.inCastsAddEditListstore.get_iter_first()
        while _iter is not None:
            
            self.inCastsSelectedList.append(self.inCastsAddEditListstore.get_value(_iter, 0))
            
            _iter = self.inCastsAddEditListstore.iter_next(_iter)
            
        # selected writers
        _iter = self.inWritersAddEditListstore.get_iter_first()
        while _iter is not None:
            
            self.inWritersSelectedList.append(self.inWritersAddEditListstore.get_value(_iter, 0))
            
            _iter = self.inWritersAddEditListstore.iter_next(_iter)
            
        movie.director = director
        movie.writers = self.inWritersSelectedList
        movie.casts = self.inCastsSelectedList
        movie.genres = self.inGenresSelectedList
        
        session.add(movie)
        session.commit()
        
        self.root_window.set_cursor(None)
        
        return movie
    
    def inPerformAdd(self):
        
        """
        Performs the actual inventory add. This method updates both GUI 
        and the database.
        """
        
        self.set_cursor("watch")
        
        movie = Movie(self.inTitleEntry.get_text(), self.inImdbCodeEntry.get_text(),
            self.inReleaseCalendar.get_date(), self.inPlotEntry.get_text(),
            self.inRatingSpin.get_value(), self.inRentalCostSpin.get_value(),
            self.inAllottedDaysSpin.get_value(), self.inStatusCombobox.get_active())
        
        self.inGenresSelectedList = []
        self.inCastsSelectedList = []
        self.inWritersSelectedList = []
        
        try:
            
            director = session.query(Director).filter(Director.full_name==self.inDirectorEntry.get_text()).one()
            
        except NoResultFound:
            
            director = Director(self.inDirectorEntry.get_text())
            
        # selected genres
        _iter = self.inGenresAddEditListstore.get_iter_first()
        while _iter is not None:
            
            self.inGenresSelectedList.append(self.inGenresAddEditListstore.get_value(_iter, 0))
            
            _iter = self.inGenresAddEditListstore.iter_next(_iter)
            
        # selected casts
        _iter = self.inCastsAddEditListstore.get_iter_first()
        while _iter is not None:
            
            self.inCastsSelectedList.append(self.inCastsAddEditListstore.get_value(_iter, 0))
            
            _iter = self.inCastsAddEditListstore.iter_next(_iter)
            
        # selected writers
        _iter = self.inWritersAddEditListstore.get_iter_first()
        while _iter is not None:
            
            self.inWritersSelectedList.append(self.inWritersAddEditListstore.get_value(_iter, 0))
            
            _iter = self.inWritersAddEditListstore.iter_next(_iter)
            
        movie = insertMovie(session, movie, director, self.inWritersSelectedList,
            self.inCastsSelectedList, self.inGenresSelectedList)
        
        self.update_inListstore([movie])
        
        self.root_window.set_cursor(None)
        
    def cuPerformAdd(self):
        
        """
        Performs the actual customer add. This method updates both GUI 
        and the database.
        """
        
        self.set_cursor("watch")
        
        gender = {_("Male"):1, _("Female"):2}
        
        gnModel = self.cuGenderCombobox.get_model()
        gnActive = self.cuGenderCombobox.get_active()
        ciModel = self.cuCityCombobox.get_model()
        ciActive = self.cuCityCombobox.get_active()
        saModel = self.cuStateCombobox.get_model()
        saActive = self.cuStateCombobox.get_active()
        coModel = self.cuCountryCombobox.get_model()
        coActive = self.cuCountryCombobox.get_active()
        
        ln = self.cuLastnameEntry.get_text()
        fn = self.cuFirstnameEntry.get_text()
        mn = self.cuMiddlenameEntry.get_text()
        st = self.cuStreetEntry.get_text()
        zi = self.cuZipcodeEntry.get_text()
        cn = PREFIX + self.cuContactnumberEntry.get_text()
        gn = gender[gnModel[gnActive][0]]
        ci = ciModel[ciActive][0]
        sa = saModel[saActive][0]
        co = coModel[coActive][0]
        
        temp_cust = Customer(ln, fn, mn, gn, cn, st, zi)
        temp_cust = insertCustomer(session, temp_cust, ci, sa, co)
        
        self.update_cuListstore([temp_cust])
        
        self.root_window.set_cursor(None)
        
    def rePerformRental(self, customer):
        
        self.reNotebook.set_current_page(1)
        
        self.reCuCode.set_label("<span foreground='blue'><b>%s</b></span>" % customer.id)
        self.reCuName.set_label("<span foreground='blue'><b>%s</b></span>" % customer.full_name)
        self.reCuAddress.set_label("<span foreground='blue'><b>%s, %s</b></span>" % (customer.street, customer.city.name))
        self.reCuAddress2.set_label("<span foreground='blue'><b>%s %s   %s</b></span>" % 
            (customer.zip_code, customer.state.name, customer.country.name))
        
        
    def update_inListstore(self, movieList):
        
        """
        Updates the inventory ListStore.
        """
        
        for instance in movieList:
            
            movie = []
            
            movie.append(instance)
            movie.append(instance.id)
            movie.append(instance.id)
            movie.append(instance.title + " (%s)" % instance.release[0:4])
            movie.append(list2str(instance.genres))
            movie.append(instance.director.full_name)
            
            self.inListstore.append(movie)
            
    def update_cuListstore(self, cuList):
        
        """
        Updates the customer ListStore.
        """
        
        gender = {1:_("(M)"), 2:_("(F)")}
        
        for instance in cuList:
            
            customer = []
            
            customer.append(instance)
            customer.append(instance.id)
            customer.append(instance.id)
            customer.append("%s %s" % (instance.full_name, gender[instance.gender]))
            customer.append(instance.contact_number)
            customer.append(instance.street)
            customer.append(instance.city.name)
            customer.append(instance.state.name)
            customer.append(instance.zip_code)
            customer.append(instance.country.name)
            
            self.cuListstore.append(customer)
            
    def update_reCuListstore(self, cuList):
        
        """
        Updates the rental ListStore.
        """
        
        gender = {1:_("(M)"), 2:_("(F)")}
        
        for instance in cuList:
            
            customer = []
            
            customer.append(instance)
            customer.append(instance.id)
            customer.append(instance.id)
            customer.append("%s %s" % (instance.full_name, gender[instance.gender]))
            customer.append(instance.contact_number)
            customer.append(instance.street)
            customer.append(instance.city.name)
            customer.append(instance.state.name)
            customer.append(instance.zip_code)
            customer.append(instance.country.name)
            
            self.reCuListstore.append(customer)
            
    def update_reInListstore(self, inList):
        
        for instance in inList:
            
            movie = []
            
            movie.append(instance)
            movie.append(instance.id)
            movie.append(instance.id)
            movie.append(instance.title + " (%s)" % instance.release[0:4])
            movie.append(instance.allotted)
            movie.append(str(instance.rent) + ".00")
            
            self.reInListstore.append(movie)
            
    def populate_inListstore(self):
        
        for instance in session.query(Movie):
            
            movie = []
            
            movie.append(instance)
            movie.append(instance.id)
            movie.append(instance.id)
            movie.append(instance.title + " (%s)" % instance.release[0:4])
            movie.append(list2str(instance.genres))
            movie.append(instance.director.full_name)
            
            self.inListstore.append(movie)
            
    def populate_cuListstore(self):
        
        gender = {1:_("(M)"), 2:_("(F)")}
        
        for instance in session.query(Customer):
            
            customer = []
            
            customer.append(instance)
            customer.append(instance.id)
            customer.append(instance.id)
            customer.append("%s %s" % (instance.full_name, gender[instance.gender]))
            customer.append(instance.contact_number)
            customer.append(instance.street)
            customer.append(instance.city.name)
            customer.append(instance.state.name)
            customer.append(instance.zip_code)
            customer.append(instance.country.name)
            
            self.cuListstore.append(customer)
            
    def add_image(self, parent, filename, text):
        
        box1 = gtk.VBox(False, 0)
        box1.set_border_width(2)
        
        image = gtk.Image()
        image.set_from_file(os.path.join(self.local_path, "img", filename))
        
        label = gtk.Label()
        label.set_text_with_mnemonic(text)
        
        box1.pack_start(image, False, False, 3)
        box1.pack_start(label, False, False, 3)
        
        image.show()
        label.show()
        
        return box1
        
    def show_loginDialog(self):
        
        ret_value = -1
        
        wTree = gtk.glade.XML(self.gladefile, "loginDialog")
        
        self.loginDialog     = wTree.get_widget("loginDialog")
        
        self.loUsernameEntry = wTree.get_widget("loUsernameEntry")
        self.loPasswordEntry = wTree.get_widget("loPasswordEntry")
        
        self.loUsernameLabel = wTree.get_widget("loUsernameLabel")
        self.loPasswordLabel = wTree.get_widget("loPasswordLabel")
        
        self.loWidgets = \
        [
            [self.loUsernameEntry, self.loUsernameLabel, _("_Username:")], 
            [self.loPasswordEntry, self.loPasswordLabel, _("_Password:")], 
        ]
        
        self.loUsernameEntry.set_activates_default(True)
        self.loPasswordEntry.set_activates_default(True)
        
        result = self.loginDialog.run()
        
        while result == gtk.RESPONSE_OK and self.validate_widgets(self.loWidgets) == -1:
            
            result = self.loginDialog.run()
            
            self.reset_widgets(self.loWidgets, False)
            
        if (result == gtk.RESPONSE_OK):
            
            username = self.loUsernameEntry.get_text()
            password = self.loPasswordEntry.get_text()
            
            u = User(username, password)
            
            try:
                user = session.query(User).filter(User.username==username).one()
                
                if u.password == user.password:
                    
                    ret_value = 0
                    
            except NoResultFound:
                
                pass
                
        elif (result == gtk.RESPONSE_CANCEL or result == gtk.RESPONSE_DELETE_EVENT):
            
            ret_value = 1
            
        self.loginDialog.hide()
        
        return ret_value
    
    def set_cursor(self, value):
        
        cursor_dict = {"watch":gtk.gdk.WATCH}
        
        cursor = gtk.gdk.Cursor(cursor_dict[value])
        
        self.root_window.set_cursor(cursor)
        
    def security(self):
        
        tries = 3
        
        while tries != 0:
             
            ret_value = self.show_loginDialog()
            
            if ret_value != 0 and ret_value != 1:
                
                tries -= 1
                
            elif ret_value == 1:
                
                sys.exit(0)
                
            else:
                
                break
            
        if ret_value != 0:
            
            sys.exit(1)
    def get_moviesByCast(self, regex, movie, movieList):
        
        for cast in movie.casts:
            
            if regex.search(cast.full_name) and movie not in movieList:
                
                movieList += [movie]
                
        return movieList
    
def list2str(li):
    
    string = ""
    for l in li:
        
        string += l.name
        
        if l != li[-1]:
            
            string += ', '
            
    return string
    
if __name__ == "__main__":

    posvrsys = POSvrSys()
    
    gtk.main()
    
