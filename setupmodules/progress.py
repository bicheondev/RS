import gtk
import sys
import foundation
import constants
import time
import upgrade
import rpm
import os
import pango
import maindialog

#JSH: for processing korean...
from rhpl.translate import _, textdomain, addPoPath

class progress:
    def set_percent(self, fraction):
	self.progress.set_fraction(fraction)
	self.progress.set_text("%3d%%" % int(fraction * 100))
	gtk.gdk.flush()
	while gtk.events_pending():
	    gtk.main_iteration(False)

    def done(self, err):
	self.buttonGroup.remove(self.backButton)
	self.buttonGroup.remove(self.nextButton)
	self.buttonGroup.remove(self.cancelButton)

	self.finishButton=gtk.Button()
	self.finishButton.set_label(_("Exit(_Q)"))
	try:
	    image = gtk.Image()
	    image.set_from_stock(gtk.STOCK_QUIT, 1)
	    self.finishButton.set_image(image)
	except:
	    pass
	self.finishButton.connect("clicked", self.exitProgram, None)

	self.buttonGroup.pack_start(self.finishButton)
	self.buttonGroup.show_all()

	self.install_state_label.set_label(_("Upgrading is finished."))

	neededspace = {}
	if err != None:
	    for (descr, (errtype, mount, need)) in err:
		if errtype == rpm.RPMPROB_DISKSPACE:
		    neededspace[mount] = need
	else:
	    msg = gtk.MessageDialog(self.parent, gtk.DIALOG_MODAL,
        			    gtk.MESSAGE_INFO, gtk.BUTTONS_OK, _("Upgrading is finished."))
    	    msg.set_position(gtk.WIN_POS_CENTER)
	    msg.run()
	    msg.destroy()

    def exitProgram(self, button, event):
	sys.exit(0)
    
    def draw_progress_image(self):

	if self.current_progress_image:
	    self.bgfixed.remove(self.current_progress_image)
	    self.current_progress_image = None
	image = maindialog.getImage("rnotes/progress%02d_3.png" % self.pstep, autoscale = True)
	self.bgfixed.put(image, maindialog.getPercentPosX(406), maindialog.getPercentPosY(223))
	self.current_progress_image = image

	image.show()
	gtk.gdk.flush()
	while gtk.events_pending():
	    gtk.main_iteration(False)
    
    def set_progress_picture(self):
	tmptime = time.time()
	if tmptime - self.currenttime >= 30:
	    self.currenttime = tmptime
	    self.pstep = self.pstep + 1
	    if self.pstep > 10:
		self.pstep = 1
	    self.draw_progress_image()

    def instcb(self, what, amount, total, h, (param)):
	self.set_progress_picture()
	self.hdr = h
	if what == rpm.RPMCALLBACK_INST_OPEN_FILE:
	    self.percentOffset = param("%s-%s-%s.%s.rpm" % (h['n'], h['v'], h['r'], h['arch']))
	    self.fd = -1
	    fn = constants.getFilename("RedStar/RPMS/%s-%s-%s.%s.rpm" % (h['n'], h['v'], h['r'], h['arch']))
	    if self.skip:
#		constants.ts.__init__()
#		constants.ts.clean()
		self.cursize += self.hdr[rpm.RPMTAG_ARCHIVESIZE]
		param(_("Cancel Install\n"), self.percentOffset)
		return 0
	    while self.fd < 0:
		try:
		    self.fd = os.open(fn, os.O_RDONLY)
		    gtk.gdk.flush()
		    while gtk.events_pending():
			gtk.main_iteration(False)
		    return self.fd
		except:
		    param(_("open failed\n"), self.percentOffset)
		    while 1:
			msg = gtk.MessageDialog(self.parent, gtk.DIALOG_MODAL,
        				gtk.MESSAGE_ERROR, gtk.BUTTONS_NONE, _("Error is occured while processing installation."))
			msg.add_button(_("Retry"), 100)
			msg.add_button(_("Cancel Install"), 101)
			msg.set_position(gtk.WIN_POS_CENTER)
			rc = msg.run()
			msg.destroy()
			if rc == 101:
			    confirmmsg = gtk.MessageDialog(self.parent, gtk.DIALOG_MODAL,
        			    gtk.MESSAGE_WARNING, gtk.BUTTONS_OK_CANCEL, _("Abort install?"))
			    confirmmsg.set_position(gtk.WIN_POS_CENTER)
			    if confirmmsg.run() == gtk.RESPONSE_OK:
				self.skip = True
				self.cursize += self.hdr[rpm.RPMTAG_ARCHIVESIZE]
				self.set_percent(float(self.cursize) / constants.totalsize)
				param(_("Cancel Install\n"), self.percentOffset)
				confirmmsg.destroy()
				os.exit(0)
				return 0
			    confirmmsg.destroy()
			    continue
			break
		    gtk.gdk.flush()
		    while gtk.events_pending():
			gtk.main_iteration(False)
#		self.cursize += self.hdr[rpm.RPMTAG_ARCHIVESIZE]
#		self.set_percent(float(self.cursize) / constants.totalsize)

		if self.fd > 0:
		    os.close(self.fd)
		param(_("Cancel Install\n"), self.percentOffset)
#		return 0

	elif what == rpm.RPMCALLBACK_INST_PROGRESS:
	    param("%d%%" % int(float(amount) / total * 100), self.percentOffset, "blue_foreground")
	    self.set_percent(float(self.cursize + amount) / constants.totalsize)

	elif what == rpm.RPMCALLBACK_INST_CLOSE_FILE:

	    if self.fd > 0:
		self.cursize += self.hdr[rpm.RPMTAG_ARCHIVESIZE]
		os.close(self.fd)
		param(_("Exit Install\n"), self.percentOffset, "blue_foreground")
	    self.set_percent(float(self.cursize) / constants.totalsize)

	elif ((what == rpm.RPMCALLBACK_UNPACK_ERROR) or (what == rpm.RPMCALLBACK_CPIO_ERROR)):
	    self.cursize += self.hdr[rpm.RPMTAG_ARCHIVESIZE]
	    self.set_percent(float(self.cursize) / constants.totalsize)
	    param("install failed\n", self.percentOffset)

	    while 1:
		msg = gtk.MessageDialog(self.parent, gtk.DIALOG_MODAL,
        			    gtk.MESSAGE_ERROR, gtk.BUTTONS_NONE, _("Error is occured while processing installation."))
		msg.add_button(_("Skip"), 100)
		msg.add_button(_("Cancel Install"), 101)
		msg.set_position(gtk.WIN_POS_CENTER)
		rc = msg.run()
		msg.destroy()
		if rc == 101:
		    confirmmsg = gtk.MessageDialog(self.parent, gtk.DIALOG_MODAL,
        			    gtk.MESSAGE_WARNING, gtk.BUTTONS_OK_CANCEL, _("Abort install?"))
		    confirmmsg.set_position(gtk.WIN_POS_CENTER)
		    if confirmmsg.run() == gtk.RESPONSE_OK:
			self.skip = True
			confirmmsg.destroy()
			os.exit(0)
			break
		    confirmmsg.destroy()
		    continue
		break
	gtk.gdk.flush()
	while gtk.events_pending():
	    gtk.main_iteration(False)

    def resultcb(self, text, offset = -1, color = "red_foreground"):
	self.resultView_Buffer = self.resultView.get_buffer()
	iter = None
	if offset != -1:
	    iter = self.resultView_Buffer.get_iter_at_offset(offset)
	    self.resultView_Buffer.delete(iter, self.resultView_Buffer.get_end_iter())
	    self.resultView_Buffer.insert_with_tags_by_name(iter, "\n" + text, color, "right_justify", "superscript")
	else:
	    iter = self.resultView_Buffer.get_end_iter()
	    self.resultView_Buffer.insert(iter, text)
	self.resultView.scroll_to_iter(self.resultView_Buffer.get_end_iter(), 0.0)
	return self.resultView_Buffer.get_end_iter().get_offset()

    def getscreen(self, foundation_obj):
	self.subfixed = foundation_obj.subfixed
	self.parent = foundation_obj.fixedWin
	self.nextButton = foundation_obj.nextButton
	self.backButton = foundation_obj.backButton
	self.cancelButton = foundation_obj.cancelButton
	self.buttonGroup = foundation_obj.buttonGroup
	self.bgfixed = foundation_obj.bgfixed

	self.install_state_label = gtk.Label()
	self.install_state_label.set_label("갱신중")
	self.install_state_label.set_size_request(maindialog.getPercentPosX(200), -1)

	self.backButton.set_sensitive(False)
	self.nextButton.set_sensitive(False)
	self.cancelButton.set_sensitive(False)

	self.resultSW = gtk.ScrolledWindow()
	self.resultSW.set_shadow_type(gtk.SHADOW_ETCHED_OUT)
	self.resultSW.set_size_request(maindialog.getPercentPosX(620), maindialog.getPercentPosY(250))
	self.resultView = gtk.TextView()
	self.resultView.set_editable(False)
	
	self.resultView_Buffer = self.resultView.get_buffer()
	self.resultView_Buffer.create_tag("red_foreground", foreground = "red")
	self.resultView_Buffer.create_tag("blue_foreground", foreground = "blue")
	self.resultView_Buffer.create_tag("right_justify", justification = gtk.JUSTIFY_RIGHT)
	self.resultView_Buffer.create_tag("superscript", rise = 10 * pango.SCALE, size = 8 * pango.SCALE)

	self.resultSW.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
	self.resultSW.add(self.resultView)

	self.progress=gtk.ProgressBar()
	self.progress.set_size_request(maindialog.getPercentPosX(200), maindialog.getPercentPosY(20))

	self.bgfixed.put(self.install_state_label, maindialog.getPercentPosX(45), maindialog.getPercentPosY(670))
	self.bgfixed.put(self.progress, maindialog.getPercentPosX(45), maindialog.getPercentPosY(640))
#	self.subfixed.put(self.resultSW, 50, 80)


	self.progress.show()
	self.install_state_label.show()
#	self.bgfixed.show_all()
	self.subfixed.show_all()
	self.install()
	return self.subfixed

    def install(self):
	buffer = self.resultView.get_buffer()
	
	gtk.gdk.flush()
	while gtk.events_pending():
	    gtk.main_iteration(False)

	self.cursize = 0
	self.skip = False
	self.currenttime = time.time()
	self.pstep = 1

	self.current_progress_image = None

	self.draw_progress_image()
	err = upgrade.upgrade(self.instcb, self.resultcb, constants.upgradepkgs, constants.hdlist)

	neededspace = 0
	if err != None:
	    for (descr, (errtype, mount, need)) in err:
		if errtype == rpm.RPMPROB_DISKSPACE:
		    neededspace = need

	errstring = ""

	if neededspace != 0:
	    errstring = _("%dMB needed.") % ((neededspace + 1024 * 1024 - 1)/ 1024 / 1024)
	    msg = gtk.MessageDialog(self.parent, gtk.DIALOG_MODAL,
        			    gtk.MESSAGE_INFO, gtk.BUTTONS_OK, errstring)
    	    msg.set_position(gtk.WIN_POS_CENTER)
	    msg.run()
	    msg.destroy()
	    sys.exit(0)

	if self.current_progress_image:
	    self.bgfixed.remove(self.current_progress_image)
	    self.current_progress_image = None
	self.progress.destroy()
	self.install_state_label.destroy()
#	self.done(err)
	self.nextButton.clicked()
