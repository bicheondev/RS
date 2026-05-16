
import gtk
import sys
import constants
import maindialog

#JSH: for processing korean...
from rhpl.translate import _, textdomain, addPoPath

argList = {
    "maindialog": ("self"),
    "confirm": ("self"),
    "progress": ("self"),
    "finish": ("self")
}

stepList = (
    "maindialog",
    "confirm",
    "progress",
    "finish",
)

stepindexDict = {
    "maindialog" : 1,
    "confirm" : 1,
    "progress" : 4,
    "finish" : 5
}

stepToclass = {
    "maindialog": ("maindialog","mainDialog"),
    "confirm": ("confirm","confirm"),
    "progress": ("progress","progress"),
    "finish": ("finish","finish")
}

class foundation:
    def __init__(self):
	self.stepImages = []
	self.step = 0

	if constants.rebooted:
	    self.step = 1

	self.max_key=3
	self.key=None
	self.t=1
	self.p=0
	self.bgscreen=gtk.Window()
	self.bgscreen.set_size_request(469, 251)
	self.bgscreen.set_resizable(False)
	self.bgscreen.set_skip_taskbar_hint(True)
	
	self.bgscreen.connect("delete_event", self.onExit)
	self.bgscreen.connect("key_press_event", self.keyEvent)
	
	self.bgscreen.set_title("")
	self.bgscreen.set_position(gtk.WIN_POS_CENTER)
#	self.bgscreen.modify_bg(gtk.STATE_NORMAL, gtk.gdk.color_parse("#446c8f"))
#	self.bgscreen.modify_base(gtk.STATE_NORMAL, gtk.gdk.color_parse("#446c8f"))

	style = self.bgscreen.get_style()
	style.bg[0] = gtk.gdk.color_parse("#c0e0ff")
	self.bgscreen.set_style(style)

	self.bgfixed = gtk.Fixed()

	self.buttonGroup = gtk.HButtonBox()
	self.buttonGroup.set_layout(gtk.BUTTONBOX_END)
	self.buttonGroup.set_spacing(10)

#	bgImage=maindialog.getImage("background.png", gtk.gdk.screen_width(), gtk.gdk.screen_height())
	bgImage=maindialog.getImage("background.png", 469, 251)

	self.bgscreen.set_app_paintable(True)
	self.bgscreen.realize()
	self.bgscreen.show_all()
	self.bgfixed.put(bgImage, 0, 0)
#	self.bgscreen.window.set_back_pixmap(bgImage.get_pixmap()[0], False)

	self.fixedWin = self.bgscreen
	try:
	    self.fixedWin.set_icon_from_file(constants.realpath + "/setupmodules/pixmaps/install.png")
	except:
	    pass
#	self.fixedWin.connect("delete-event", self.close, None)
#	self.fixedWin.set_parent_window(self.bgscreen.window)
#	self.fixedWin.set_modal(True)

#	self.fixedWin.set_title("Upgrade")
#	self.fixedWin.set_transient_for(self.bgscreen)
#	self.fixedWin.set_position(gtk.WIN_POS_CENTER)
#	self.fixedWin.set_resizable(0)
#	self.fixedWin.resize(500, 400)
	
	try:
    	    version = "%s%s" % ( open( "%s/.discinfo" % constants.realpath, "r" ).read().split("\n")[1], _(" Setup"))
	except:
    	    version = _("RedStar3.0_Install")
	
	self.fixedWin.set_title(version)
	
	try:
	    self.fixedWin.set_icon_from_file ( '/usr/share/icons/hicolor/32x32/apps/kmenu.png' )
	    #import os
	    #os.system ( "preview /usr/share/icons/hicolor/32x32/apps/kmenu.png" )
	except:
	    #print "can not read redstar icon"
	    pass
	
	self.vbox = gtk.VBox()
	self.vbox.set_size_request(500, 400)
	
	self.subfixed = gtk.Fixed()
	
	try:
	    image = gtk.Image()
	    image.set_from_stock(gtk.STOCK_QUIT, 1)
	    self.finishButton.set_image(image)
	except:
	    pass
	    
	self.buttonGroup.set_border_width(10)
	
	self.subfixed.set_size_request(maindialog.getPercentPosX(132), maindialog.getPercentPosY(268))
	self.bgfixed.put(self.subfixed, maindialog.getPercentPosX(0), maindialog.getPercentPosY(0))
#	self.bgfixed.put(self.buttonGroup, 250, 173)
	self.bgfixed.put(self.buttonGroup, 140, 173)
	
	self.vbox.pack_start(self.bgfixed, True)
#	self.vbox.pack_start(self.buttonGroup, False)
	
	self.fixedWin.add(self.vbox)
	self.fixedWin.show_all()
	
	gtk.gdk.flush()
	while gtk.events_pending():
	    gtk.main_iteration(False)
	    
	self.backButton = gtk.Button()
	self.nextButton = gtk.Button()
	self.cancelButton = gtk.Button()
	#self.spaceButton = gtk.Button()
	self.exitButton = gtk.Button()
	self.finishButton=gtk.Button()
	
	self.buttonGroup.pack_start(self.backButton)
	self.buttonGroup.pack_start(self.nextButton)
	self.buttonGroup.pack_start(self.cancelButton)
	#self.buttonGroup.pack_start(self.spaceButton)
	self.buttonGroup.pack_start(self.exitButton)
	self.buttonGroup.pack_start(self.finishButton)
	
	self.backButton.set_label(_("Previous"))
	self.backButton.connect("clicked", self.onBack)
	self.backButton.hide()
	
	self.nextButton.set_label(_("Next"))
	self.nextButton.connect("clicked", self.onNext)
	self.nextButton.hide()

	self.cancelButton.set_label(_("Cancel"))
	self.cancelButton.connect("clicked", self.onCancel)
	self.cancelButton.hide()

	self.exitButton.set_label(_("Finish"))
	self.exitButton.connect("clicked", self.onCancel)
	
	try:
	    self.exitButton.set_use_custom_size()
	except:
	    print "can not find func: set_use_custom_size"
	
	self.exitButton.set_size_request(78, 30)
	self.exitButton.hide()

	self.finishButton.set_label(_("Done"))
	self.finishButton.hide()
	self.finishButton.connect("clicked", self.onCancel)

    def getscreen(self):
	newclassname=None
	self.key=stepList[self.step]

	(file,classname) = stepToclass[self.key]
	args = argList[self.key]

	s = "from %s import %s; newclassname = %s" % (file,classname,classname)

	exec s

	obj = newclassname()

	s = "self.fixedresult = obj.getscreen(%s)" % args

	children = self.subfixed.get_children()
	if children:
	    for i in children:
		self.subfixed.remove(i)
		i.destroy()
#added by rki
	currentStep = stepindexDict[self.key]
	stepindex = 1
	self.pos = maindialog.getPercentPosY(150+70*stepindex)
	for i in self.stepImages:
	    self.bgfixed.remove(i)
	    del i
	self.stepImages.__init__()
	self.bgfixed.show()
	self.buttonGroup.show()
	self.subfixed.show()
	self.fixedWin.show()
	exec s

    def onBack(self, button):
	if self.step <= self.max_key:
	    self.nextButton.set_sensitive(True)

	if self.step == 1:
	    self.t = 0

	self.step -= 1

#	if self.step == 0:
#	    self.bgscreen.destroy()
#	    self.fixedWin.destroy()

	self.getscreen()

    def onNext(self, button):
	self.step += 1

	if self.step == self.max_key:
	    button.set_sensitive(False)

	self.getscreen()

    def onCancel(self, button):
	sys.exit(0)

    def onExit(self, window, event):
	sys.exit(0)

    def keyEvent(self, window, event):
	if event.keyval == 0xff1b:
	    sys.exit(0)

    def getImage(self, imgpath):
	image = gtk.Image()
	image.set_from_file(constants.realpath + "/setupmodules/pixmaps/" + imgpath)
	return image

    def close(self, window, event, data):
	return True


    def backButton_sensitive(self, v):
	self.backButton.set_sensitive(v)
    
    def nextButton_sensitive(self, v):
	self.nextButton.set_sensitive(v)
    
    def cancelButton_sensitive(self, v):
	self.cancelButton.set_sensitive(v)
    
    def exitButton_sensitive(self, v):
	self.exitButton.set_sensitive(v)
    
    def backButton_show(self, v):
	if v:
	    self.backButton.show()
	else:
	    self.backButton.hide()

    def nextButton_show(self, v):
	if v:
	    self.nextButton.show()
	else:
	    self.nextButton.hide()

    def cancelButton_show(self, v):
	if v:
	    self.cancelButton.show()
	else:
	    self.cancelButton.hide()

    def exitButton_show(self, v):
	if v:
	    self.exitButton.show()
	else:
	    self.exitButton.hide()

    def finishButton_show(self, v):
	if v:
	    self.finishButton.show()
	else:
	    self.finishButton.hide()
