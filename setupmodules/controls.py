#!/usr/bin/python
import constants
import os
import gtk
from gtk import gdk
import math
import gobject
import string

#JSH: for processing korean...
from rhpl.translate import _, textdomain, addPoPath

def titleBarMousePressCB(widget, event, data):
    if event.type & gtk.gdk.BUTTON_PRESS:
	data["state"] = 1
	data["button"] = event.button
	data["deltax"] = event.x
	data["deltay"] = event.y
	
def titleBarMouseReleaseCB(widget, event, data):
    if data["state"] and event.button == data["button"]:
	data["state"] = 0
	data["button"] = 0
	data["deltax"] = 0
	data["deltay"] = 0

def titleBarMotionEventCB(widget, event, data):
    if data["state"]:
	newx = event.x_root-data["deltax"]
	newy = event.y_root-data["deltay"]
	if newx < 0:
	    newx = 0
	if newy < 0:
	    newy = 0
	(w, h) = data["window"].get_size()
	if (newx + w) > gtk.gdk.screen_width():
	    newx = gtk.gdk.screen_width() - w
	if (newy + 20) > gtk.gdk.screen_height():
	    newy = gtk.gdk.screen_height() - 20

	data["window"].move( int( newx ), int( newy ) )

class MessageWindow:
    
    def __init__( self, parentWindow, szContent, messageType = gtk.MESSAGE_INFO, buttonsType = [ ("OK") ] ):
		
	gtk.gdk.get_default_root_window().set_cursor( gtk.gdk.Cursor( gtk.gdk.LEFT_PTR ) ) 
	#dlg = gtk.MessageDialog( None, 0, messageType, gtk.BUTTONS_NONE, szContent )
	dlg = gtk.MessageDialog( parentWindow, gtk.DIALOG_MODAL, messageType, gtk.BUTTONS_NONE, szContent )
	dlg.set_border_width(0)
	
	#msg = gtk.MessageDialog ( self.parent_window, gtk.DIALOG_MODAL,
        #                       gtk.MESSAGE_QUESTION, gtk.BUTTONS_OK_CANCEL, _("Rebooting is needed for installation, continue rebooting?") )
	
	#dlg.set_position( gtk.WIN_POS_CENTER )
	dlg.set_decorated( False )
	dlg.set_modal( True )
	
	focusButton = None
	defaultButton = None

	for i in range( len( buttonsType ) ):
    	    lastBtn = dlg.add_button( buttonsType[i], i )
    	    
    	    try:
    	    	lastBtn.set_use_custom_size()
    	    except:
    	    	print "can not find func: set_use_custom_size"
    	    
	    if i == 0:
		focusButton = lastBtn
	    else:
		defaultButton = lastBtn

    	    lastBtn.set_size_request ( 75, 30 )
        mainContents = dlg.get_children()[0]
        dlg.remove( mainContents )
	
	imgTitleBar = gtk.Image()
	try:
	    #imgTitleBar.set_from_pixbuf( gtk.gdk.pixbuf_new_from_file( "./setupmodules/pixmaps/titlebar.png" ) )
	    imgTitleBar.set_from_pixbuf( gtk.gdk.pixbuf_new_from_file( constants.realpath + "/setupmodules/pixmaps/titlebar.png" ) )
	    #print constants.realpath
	except:
	    pass
	imgTitleBar.set_size_request( 200, -1 )
	
	evtTitleBar = gtk.EventBox()
	evtTitleBar.set_border_width(0)
	
	data = {}
	data["state"] = 0
	data["button"] = 0
	data["deltax"] = 0
	data["deltay"] = 0
	data["window"] = dlg
	
	evtTitleBar.connect( "button-press-event", titleBarMousePressCB, data )
	evtTitleBar.connect( "button-release-event", titleBarMouseReleaseCB, data )
	evtTitleBar.connect( "motion-notify-event", titleBarMotionEventCB, data )
	
	evtTitleBar.add( imgTitleBar )
	
	padding_lbl1 = gtk.Label()
	padding_lbl1.set_size_request ( -1, 10 )
	padding_lbl2 = gtk.Label()
	padding_lbl2.set_size_request ( -1, 5 )
	
        mainContainer = gtk.VBox()
        mainContainer.set_border_width(0)
        mainContainer.pack_start( evtTitleBar )
        mainContainer.pack_start( padding_lbl1 )
        mainContainer.pack_start( mainContents )
	mainContainer.pack_start( padding_lbl2 )
	
	frmContainer = gtk.Frame()
	frmContainer.set_border_width(0)
	frmContainer.add( mainContainer )
	
	#frmContainer.set_shadow_type ( gtk.SHADOW_NONE )
	frmContainer.set_shadow_type ( gtk.SHADOW_IN )
	
#	lastBtn.grab_focus()
	dlg.add( frmContainer )
	
	if focusButton:
	    focusButton.set_flags(gtk.CAN_FOCUS)
	    focusButton.grab_focus()
	if defaultButton:
	    defaultButton.set_flags(gtk.CAN_DEFAULT)
	    defaultButton.grab_default()
    	dlg.show_all()
	self.returnCode = dlg.run()
	dlg.destroy()
	
    def getReturnCode( self ):
	return self.returnCode
	