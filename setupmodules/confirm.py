import gtk
import sys
import foundation
import gobject
import upgrade
import time
import constants
import maindialog

#JSH: for processing korean...
from rhpl.translate import _, textdomain, addPoPath

class confirm:

    def make_treeview(self, sw):
    
	self.lstore =  gtk.ListStore(gobject.TYPE_BOOLEAN,
				gobject.TYPE_STRING,
				gobject.TYPE_STRING,
				gobject.TYPE_STRING)

	self.treeview = gtk.TreeView(self.lstore)

	checkboxRenderer = gtk.CellRendererToggle()
	checkboxRenderer.connect("toggled", self.fixed_toggled, self.lstore)

	column = gtk.TreeViewColumn(_("Upgrade"), checkboxRenderer, active=0)
	column.set_sort_column_id(0)
	column.set_clickable(False)
	column.set_resizable(False)
	self.treeview.append_column(column)

	column = gtk.TreeViewColumn(_("Name"), gtk.CellRendererText(), text=1)
	column.set_sort_column_id(1)
	column.set_resizable(True)
	self.treeview.append_column(column)

	column = gtk.TreeViewColumn(_("Copyright"), gtk.CellRendererText(), text=2)
	column.set_sort_column_id(2)
	column.set_resizable(True)
	self.treeview.append_column(column)

	column = gtk.TreeViewColumn(_("Summary"), gtk.CellRendererText(), text=3)
	column.set_sort_column_id(3)
	column.set_resizable(True)
	self.treeview.append_column(column)
	sw.add(self.treeview)

    def fixed_toggled(self, cell, path, model):
	iter = model.get_iter((int(path), ))
	fixed = model.get_value(iter, 0)
	fixed = not fixed
	model.set(iter, 0, fixed)
	
	if fixed:
	    name = model.get_value(iter, 1)
	    vra = model.get_value(iter, 2)
	    for i in constants.upgradepkgs:
		if i['name'] == name and vra == "%s-%s.%s" % (i['v'], i['r'], i['arch']):
		    return
	    for i in constants.upgradables:
		if i['name'] == name and vra == "%s-%s.%s" % (i['v'], i['r'], i['arch']):
		    constants.upgradepkgs.append(i)
		    print "Appended:", i['Name']
		    self.nextButton.set_sensitive(True)
	else:
	    name = model.get_value(iter, 1)
	    vra = model.get_value(iter, 2)
	    for i in constants.upgradepkgs:
		if i['name'] == name and vra == "%s-%s.%s" % (i['v'], i['r'], i['arch']):
		    constants.upgradepkgs.remove(i)
		    print "Removed:", i['Name']
	    if len(constants.upgradepkgs) == 0:
		self.nextButton.set_sensitive(False)

    def getscreen(self, foundation_obj):

	subfixed=foundation_obj.subfixed
	self.parent = foundation_obj.fixedWin

	buttonGroup = foundation_obj.buttonGroup
	self.backButton = foundation_obj.backButton

	foundation_obj.exitButton.hide()
	foundation_obj.finishButton.hide()
	foundation_obj.nextButton.show()
	foundation_obj.backButton.hide()
	foundation_obj.cancelButton.show()

	buttonGroup.set_sensitive(False)

	self.label = gtk.Label()
	self.label.set_justify(gtk.JUSTIFY_CENTER)
	self.label.set_alignment(0.5, 0.5)

	if subfixed.window:
	    subfixed.window.set_cursor(gtk.gdk.Cursor(gtk.gdk.WATCH))
	self.label.modify_fg(gtk.STATE_NORMAL, gtk.gdk.color_parse("#000000"))
	self.label.set_label(_("searching..."))

	subfixed.put(self.label, maindialog.getPercentPosX(10), maindialog.getPercentPosY(100))
	self.label.set_size_request(maindialog.getPercentPosX(700), maindialog.getPercentPosY(100))
#	subfixed.put(sw, 10, 30)

	subfixed.show_all()

	gtk.gdk.flush()
	while gtk.events_pending():
	    gtk.main_iteration(False)

	hdrlist = upgrade.getUpgradable()
	constants.upgradepkgs.__init__()

	for i in hdrlist:
	    gtk.gdk.flush()
	    while gtk.events_pending():
		gtk.main_iteration(False)
	    constants.upgradepkgs.append(i)

	self.label.set_label(_("for upgrade, click Next"))
	if subfixed.window:
	    subfixed.window.set_cursor(gtk.gdk.Cursor(gtk.gdk.LEFT_PTR))
	subfixed.show_all()
	gtk.gdk.flush()
	while gtk.events_pending():
	    gtk.main_iteration(False)
	buttonGroup.set_sensitive(True)

	if len(hdrlist) == 0:
	    self.label.set_label("")
	    msg = gtk.MessageDialog(self.parent, gtk.DIALOG_MODAL,
        			    gtk.MESSAGE_INFO, gtk.BUTTONS_OK, _("there is no item for upgrade."))

    	    msg.set_position(gtk.WIN_POS_CENTER)
	    msg.run()
	    msg.destroy()
	    self.backButton.clicked()

	return subfixed
