import gtk
import sys
import foundation
import maindialog
import os
import constants
import install

#JSH: for processing korean...#for processing korean...
from rhpl.translate import _, textdomain, addPoPath

class finish:

    def getscreen(self, foundation_obj):
	constants.grubInstall()
	foundation_obj.buttonGroup.remove(foundation_obj.backButton)
	foundation_obj.buttonGroup.remove(foundation_obj.nextButton)
	foundation_obj.buttonGroup.remove(foundation_obj.cancelButton)
	foundation_obj.buttonGroup.remove(foundation_obj.exitButton)
	foundation_obj.finishButton.hide()
	doneimg = maindialog.getImage("done.png", autoscale = True)
	foundation_obj.subfixed.put(doneimg, maindialog.getPercentPosX(300), maindialog.getPercentPosY(100))
	doneimg.show()
	msg = gtk.MessageDialog(foundation_obj.fixedWin, gtk.DIALOG_MODAL,
                               gtk.MESSAGE_QUESTION, gtk.BUTTONS_OK, _("Upgrading is finished. for using new system rebooting is needed. eject installation media and click OK."))

	msg.set_position(gtk.WIN_POS_CENTER)
	os.system("eject /tmp/hdimage")
	rc = msg.run()
	msg.destroy()
#	if rc == gtk.RESPONSE_YES:
	if 1:
	    os.system("dcop ksmserver ksmserver logout 0 1 1")
	    sys.exit(0)
