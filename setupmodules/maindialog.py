import controls
import gtk
import gtk.gdk
import constants
import sys
import foundation
import gobject
import pango
import os

#JSH: for processing korean...
from rhpl.translate import _, textdomain, addPoPath

def getPercentPosX(x):
    return gtk.gdk.screen_width() * x / 1024

def getPercentPosY(y):
    return gtk.gdk.screen_height() * y / 768

def getImage(imgpath, width = -1, height = -1, autoscale = False):
    image = gtk.Image()

    try:
	pixbuf = gtk.gdk.pixbuf_new_from_file(constants.realpath + "/setupmodules/pixmaps/" + imgpath)
    except:
	return image

    if autoscale:
	width = getPercentPosX(pixbuf.get_width())
	height = getPercentPosY(pixbuf.get_height())

    if width > 0 and height > 0:
	pixbuf = pixbuf.scale_simple(width, height, gtk.gdk.INTERP_BILINEAR)

    image.set_from_pixbuf(pixbuf)

    return image

class ImageButton(gtk.EventBox):
    def __init__(self, normal, pressed):
	gtk.EventBox.__init__(self)
	self.normalImage = normal
	self.pressedImage = pressed
	self.entered = False
	self.pressed = False

	self.eventButton = None

	self.image = gtk.Image()
	self.image.set_from_file(self.normalImage)
	self.add(self.image)
	self.connect("button_press_event", self.pressedFunc)
	self.connect("button_release_event", self.releasedFunc)
	self.connect("enter_notify_event", self.enteredFunc)
	self.connect("leave_notify_event", self.leavedFunc)

    def enteredFunc(self, widget, event):
	self.entered = True
	if self.pressed:
	    self.image.set_from_file(self.pressedImage)

    def leavedFunc(self, widget, event):
	self.entered = False
	if self.pressed:
	    self.image.set_from_file(self.normalImage)

    def pressedFunc(self, widget, event):
	self.pressed = True
	self.image.set_from_file(self.pressedImage)
	
	
    def releasedFunc(self, widget, event):
	if self.entered and self.eventButton:
	    self.eventButton.emit("clicked")
	self.pressed = False
	self.image.set_from_file(self.normalImage)
	
	#JSH : help action
	if self.entered:
	    helppid = os.fork()
	    if (not helppid):
		args = [ "/usr/bin/quicklook", constants.realpath + "/Guide.pdf"]
    		os.execv(args[0], args)
		sys.exit (1)
	
class instTypeButton(gtk.EventBox):
    __gsignals__ = {
	'clicked': (gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE, ())
    }
    def __init__(self, button, text):
	gtk.EventBox.__init__(self)

	self.pressed = 0
	self.actived = 0
	self.entered = 0

	hbox = gtk.HBox()
	hbox.pack_start(button, False, True, True)
	hbox.set_spacing(10)

	self.label = gtk.Label()
	
	font = pango.FontDescription("")
	font.set_size(12000)
	self.label.modify_font(font)
	
	self.label.set_label(text)
	self.label.set_justify(gtk.JUSTIFY_LEFT)
	self.label.set_alignment(0.0, 0.5)
	
	hbox.pack_start(self.label, True, True, True)
	self.add(hbox)
	self.set_visible_window(False)
	self.label.modify_fg(gtk.STATE_NORMAL, gtk.gdk.color_parse("black"))
	
	self.connect("enter_notify_event", self.enterEvent, None)
	self.connect("leave_notify_event", self.leaveEvent, None)
	self.connect("button_press_event", self.pressEvent, None)
	self.connect("button_release_event", self.releaseEvent, None)
	button.connect("clicked", self.releaseEvent, None)
	button.connect("enter_notify_event", self.enterEvent, None)
	button.connect("leave_notify_event", self.leaveEvent, None)
	
    def enterEvent(self, button, event, data = None):
	self.entered = 1
	
	if type(button) != instTypeButton:
	    self.emit("enter_notify_event", event)
	self.label.modify_fg(gtk.STATE_NORMAL, gtk.gdk.color_parse("red"))
	
    def leaveEvent(self, button, event, data = None):
	self.entered = 0
	
    	if type(button) != instTypeButton:
    	    self.emit("leave_notify_event", event)
    	self.label.modify_fg(gtk.STATE_NORMAL, gtk.gdk.color_parse("black"))
    
    def pressEvent(self, button, event, data = None):
    	self.pressed = 1
    
    def releaseEvent(self, button, event, data = None):
	if self.pressed and self.entered:
	    self.emit("clicked")
	self.pressed = 0
	
class myButton(gtk.EventBox):
    __gsignals__ = {
        'clicked': (gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE, ())
    }
    
    def __init__(self, normalPix, pressedPix, highlightPix, activePix, inactivePix, width = -1, height = -1):
	gtk.EventBox.__init__(self)
	
	self.width = width
	self.height = height
	
	self.set_visible_window(False)
	
	self.image = gtk.Image()
	self.add(self.image)
	
	self.normalPixbuf = gtk.gdk.pixbuf_new_from_file(constants.realpath + "/setupmodules/pixmaps/" + normalPix)
	self.pressedPixbuf = gtk.gdk.pixbuf_new_from_file(constants.realpath + "/setupmodules/pixmaps/" + pressedPix)
	self.highlightPixbuf = gtk.gdk.pixbuf_new_from_file(constants.realpath + "/setupmodules/pixmaps/" + highlightPix)
	self.activePixbuf = gtk.gdk.pixbuf_new_from_file(constants.realpath + "/setupmodules/pixmaps/" + activePix)
	self.inactivePixbuf = gtk.gdk.pixbuf_new_from_file(constants.realpath + "/setupmodules/pixmaps/" + inactivePix)
	
	self.currentPixbuf = self.normalPixbuf
	self.redrawButton()
	self.pressed = 0
	self.actived = 0
	self.entered = 0
	
	self.connect("button_press_event", self.pressEvent, None)
	self.connect("button_release_event", self.releaseEvent, None)
	self.connect("enter_notify_event", self.enterEvent, None)
	self.connect("leave_notify_event", self.leaveEvent, None)
	
    def enterEvent(self, button, event, data):
	self.entered = 1
	
	if self.pressed:
	    self.currentPixbuf = self.pressedPixbuf
	else:
	    self.currentPixbuf = self.highlightPixbuf
	    
	self.redrawButton()
	
    def leaveEvent(self, button, event, data):
	self.entered = 0
	
	if self.actived:
	    self.currentPixbuf = self.activePixbuf
	else:
	    self.currentPixbuf = self.normalPixbuf
	    
	self.redrawButton()
	
    def pressEvent(self, button, event, data):
	self.currentPixbuf = self.pressedPixbuf
	self.pressed = 1
	
	self.redrawButton()
	
    def releaseEvent(self, button, event, data):
	if self.actived:
	    self.currentPixbuf = self.activePixbuf
	else:
	    self.currentPixbuf = self.normalPixbuf
	    
	self.redrawButton()
	if self.entered and self.pressed:
	    self.emit("clicked")
	self.pressed = 0
    def redrawButton(self):
	pixbuf = self.currentPixbuf
	if self.width > 0 and self.height > 0:
	    pixbuf = self.currentPixbuf.scale_simple(self.height, self.width, gtk.gdk.INTERP_BILINEAR)
	    
	self.image.set_from_pixbuf(pixbuf)
	
class mainDialog:
    def getImage(self, imgpath):
	image = gtk.Image()
	image.set_from_file(constants.realpath + "/setupmodules/pixmaps/" + imgpath)
	return image
	
    def onInstall(self,button, method):
	
	import bios
	if bios.isMac( bios ):
	    m = gtk.MessageDialog(self.parent_window, gtk.DIALOG_MODAL,
	    		gtk.MESSAGE_ERROR, gtk.BUTTONS_OK, _("You are using non iMac-Setup program. \nTry again using iMac_Setup program"))
	    m.set_position(gtk.WIN_POS_CENTER)
	    m.run()
	    m.destroy()
	    return
	    
	import gobject
    	
    	#msg = gtk.MessageDialog ( self.parent_window, gtk.DIALOG_MODAL,
        #                       gtk.MESSAGE_QUESTION, gtk.BUTTONS_OK_CANCEL, _("Rebooting is needed for installation, continue rebooting?") )
    	
    	#JSH : for own messagedialog
    	msg = controls.MessageWindow( self.parent_window, (_("You need to restart the computer for a system installation.\nRestart now?"))
                                       , gtk.MESSAGE_WARNING, [ (_("No")), (_("Yes")) ] )
    	

    	rc = msg.getReturnCode()
    	
    	try:
    	    version = "%s%s" % ( open( "%s/.discinfo" % constants.realpath, "r" ).read().split("\n")[1], _(" Setup"))
	except:
    	    version = _("RedStar3.0_Install")
	
    	#JSH: old way using gtk.MessageDialog
    	"""
    	msg.set_position(gtk.WIN_POS_CENTER)
    	msg.set_title(version)
    	msg.set_icon_from_file ( '/usr/share/icons/hicolor/16x16/apps/kmenu.png' )
    	msg.add_buttons( msg, _("Yes"), gtk.BUTTONS_OK, _("No"), gtk.BUTTON_CANCEL)
    	msg.add_buttons(_("No"))
    	rc = msg.run()
    	msg.destroy()
    	"""
	
	if rc == 1: #gtk.RESPONSE_OK:
	    
	    w_cursor = gtk.gdk.Cursor(gtk.gdk.WATCH)
	    for win in gtk.gdk.window_get_toplevels():
	    	win.set_cursor(w_cursor)
	    
	    
	    if os.fork():
	    	w_cursor = gtk.gdk.Cursor(gtk.gdk.WATCH)
		for win in gtk.gdk.window_get_toplevels():
	    	    win.set_cursor(w_cursor)
	    
	    else:
	    	#gtk.gdk.get_default_root_window().set_cursor(gtk.gdk.Cursor(gtk.gdk.WATCH))
	    	import install
	    	rc = install.install(constants.realpath, "", method)
	    	if rc:
	    	    m = gtk.MessageDialog(self.parent_window, gtk.DIALOG_MODAL,
	    	    		gtk.MESSAGE_ERROR, gtk.BUTTONS_OK, _("Error is occured while preparing installation."))
	    	    		
	    	    m.set_position(gtk.WIN_POS_CENTER)
	    	    m.run()
	    	    m.destroy()
	    	    return
	    	    		
		constants.grubInstall()
		os.system("dcop ksmserver ksmserver logout 0 1 1")
		sys.exit(0)
	    
    def onUpgrade(self,button):
	#self.window.destroy()
	#foundt=foundation.foundation()
	#foundt.getscreen()

	if constants.rebooted:
	    self.installButton.destroy()
	    self.upgradeButton.destroy()
	    self.tipLabel.destroy()
	    self.nextButton.clicked()
	    return
	msg = gtk.MessageDialog(self.parent_window, gtk.DIALOG_MODAL,
                               gtk.MESSAGE_QUESTION, gtk.BUTTONS_OK_CANCEL, _("You need to restart the computer for a system installation. Eject installation media and reboot."))

	msg.set_position(gtk.WIN_POS_CENTER)
	rc = msg.run()
	msg.destroy()
	if rc == gtk.RESPONSE_OK:
	    import upgrade
	    rc = upgrade.upgradeDaemon()
	    if rc:
		msg = gtk.MessageDialog(self.parent_window, gtk.DIALOG_MODAL,
				gtk.MESSAGE_ERROR, gtk.BUTTONS_OK, _("Error is occured while preparing installation. seemed wrong installation version."))
	    
		msg.set_position(gtk.WIN_POS_CENTER)
		msg.run()
		msg.destroy()
		return

	    constants.grubInstall()
	    os.system("dcop ksmserver ksmserver logout 0 1 1")
	    sys.exit(0)

    def onhelp(self, button):
	helppid = os.fork()
	if (not helppid):
	    args = [ "/usr/bin/quicklook", constants.realpath + "/Guide.pdf"]
    	    os.execv(args[0], args)
	    sys.exit (1)
	
	    
    def getscreen(self, foundation_obj):

	self.parent_window = foundation_obj.fixedWin
    	self.HandCursor = gtk.gdk.Cursor(gtk.gdk.HAND2)
	self.NormalCursor = gtk.gdk.Cursor(gtk.gdk.LEFT_PTR)
	self.nextButton = foundation_obj.nextButton

	for i in foundation_obj.buttonGroup.get_children():
	    i.hide()
	    
	self.window = foundation_obj.subfixed
	
	self.fixed = gtk.Fixed()
	
	self.step="1"
	
	self.window.put(self.fixed, 0, 0)
	self.tipLabel = gtk.Label()
#	self.tipLabel.modify_fg(gtk.STATE_NORMAL, gtk.gdk.color_parse ("black"))
	self.fixed.put(self.tipLabel, getPercentPosX(0), getPercentPosY(220))
	self.tipLabel.set_size_request(getPercentPosX(700), getPercentPosY(100))
	self.tipLabel.set_alignment(0.5, 0.0)
	btBox = gtk.VButtonBox()
	btBox.set_layout(gtk.BUTTONBOX_START)
	btBox.set_spacing(10)
	
	self.fixed.put(btBox, getPercentPosX(200), getPercentPosY(60))
	btBox.set_size_request(getPercentPosX(140), getPercentPosY(160))
	
	self.installButton = gtk.Button()
	#self.fixed.put(self.installButton, 135, 265)
	self.fixed.put(self.installButton, 260, 183)
	self.installButton.set_label(_("Install"))
	self.installButton.grab_default()
	
	try:
	    self.installButton.set_use_custom_size()
	except:
	    print "can not find func: set_use_custom_size"
	
	self.installButton.set_size_request(88, 30)
	self.installButton.set_flags(gtk.CELL_RENDERER_FOCUSED)
	self.installButton.set_flags(gtk.CAN_FOCUS)
	self.installButton.set_flags(gtk.CAN_DEFAULT)
	self.installButton.set_flags(gtk.BUTTONS_OK)
	self.installButton.grab_focus()
	self.installButton.show()
	self.installButton.connect("clicked",self.onInstall, "hd")
	
	self.upgradeButton = gtk.Button()
	#self.fixed.put(self.upgradeButton, 135, 295)
	self.upgradeButton.set_size_request(180, 27)
	self.upgradeButton.connect("clicked",self.onInstall, "nfs")
	
	self.helpButton1 = gtk.Button()
	self.helpButton1.set_label("")
	import constants
	realpath = constants.realpath
	self.helpButton = ImageButton( realpath + "/setupmodules/theme/helpbutton_normal.png", realpath + "/setupmodules/theme/helpbutton_pressed.png")
	self.helpButton.eventButton = self.helpButton1
	#self.helpButton.show_all()
	self.fixed.put(self.helpButton, 385, 182)
	self.helpButton.set_size_request(28, 30)
	#self.helpButton.connect("clicked",self.onhelp)
	
	foundation_obj.exitButton.show()
	self.fixed.show_all()
	self.helpButton.hide()
	
	foundation_obj.exitButton.grab_focus()
	self.installButton.grab_default()

    def button_tip(self, button, event, data):
	if button.window:
	    button.window.set_cursor(self.HandCuor)
	if button == self.installButton:
	    self.tipLabel.set_label(_("Install RedStar3"))
	elif button == self.upgradeButton:
	    self.tipLabel.set_label(_("Upgrade current system."))
	elif button == self.exitButton:
	    self.tipLabel.set_label(_("Exit program."))
	    
    def button_tip_clear(self, button, event, data):
	if button.window:
	    button.window.set_cursor(self.NormalCursor)
	self.tipLabel.set_label("")
	