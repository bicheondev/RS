import os
import sys
import gtk

#JSH: for processing korean...
from rhpl.translate import _, textdomain, addPoPath

realpath = ""
prodpath = ""

upgradables = []
ts = None
provDict = None
hdlist = None
upgradepkgs = []

stamp = "1208406548.613644"

rebooted = False

mounted = False

def grubInstall():
    
    cfgfile = None
    try:
    	cfgfile = open("/boot/grub/grub.conf", "r")
    except:
    	return bootdev
    	
    buf = ""
    buf = cfgfile.read().split("\n")
    
    cfgfile.close()
    for i in buf:
    	if i.strip().startswith("#boot="):
    	    bootdev = i.strip()[6:].strip()
	
    	try:
    	    dmfile = open("/boot/grub/device.map", "r")
	except:
    	    return bootdev
    	    
    	buf = dmfile.read().split("\n")
    	dmfile.close()
    	
    	for i in buf:
    	    if i.strip().startswith("(hd0)"):
    	    	bootdev = i.strip()[5:].strip()
    
    if bootdev == "":	
    	bootdev = "/dev/sda"	
    	
    os.system("grub-install %s" % bootdev)
    return bootdev
    
def mountProdDev():
    global stamp
    global mounted

    dev = os.environ['PRODDEV']
    path = os.environ['PRODPATH']
    matched = False
    while not matched:
	os.system("mkdir /tmp/hdimage;mount %s /tmp/hdimage" % dev)
	try:
	    file = open("/tmp/hdimage/%s/.discinfo" % path, "r")
	    buf = file.read()
	    file.close()
	    matchstamp = buf.split("\n")[0]
	    if matchstamp == stamp:
		matched = True
		mounted = True
		break
	except:
	    pass
	os.system("eject %s" % dev)
	msg = gtk.MessageDialog(None, gtk.DIALOG_MODAL, gtk.MESSAGE_ERROR, gtk.BUTTONS_NONE,_("Please insert installation CD, or click Cancel to abort."))
	msg.add_buttons(_("Confirm"), 100)
	msg.add_buttons(_("Cancel"), 101)
	msg.set_position(gtk.WIN_POS_CENTER)
	if msg.run() == 101:
	    sys.exit(0)
	msg.destroy()

def ejectProdDev():
    global mounted
    if mounted:
	os.system("eject /tmp/hdimage")
	mounted = False

def getFilename(fn):
    global prodpath
    global mounted
    try:
	prodpath = os.environ['PRODPATH']
    except:
	print "Can not get product path"
    print "prodpath:%s" % prodpath
    if not mounted:
	mountProdDev()
    return os.path.realpath("/tmp/hdimage/" + prodpath + "/" + fn)
