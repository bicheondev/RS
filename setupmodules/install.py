#!/usr/bin/python

import os, sys
import constants
#import kudzu
import rhpl.iconv as iconv
import maindialog
import gtk

#JSH: we use bios rather than using dmidecode 
#import dmidecode
#for processing korean...
from rhpl.translate import _, textdomain, addPoPath

import bios

def geturl(path, level):
    mtab = []
    	
    file = open("/etc/mtab", "r")
    buf = file.read().split("\n")
    file.close()
    
    file = open("/proc/mounts", "r")
    buf1 = file.read().split("\n")
    file.close()
    buf.extend(buf1)
    
    for i in buf:
    	v = i.split()
    	if len(v) < 3:
    	    continue
    	mtab.insert(0, (v[0], v[1]))
    	
    if level > 1:
    	return (None, None, None)
    for i in mtab:
    	if os.path.isfile(path):
    	    path = os.path.dirname(path)
    	mntpt = i[1]
    	mntpt = mntpt.replace("\\040", "\040")
    	if path == mntpt and not i[0].startswith("/dev/"):
    	    rc = geturl(i[0], level + 1)
    	    return rc
    	elif path.startswith(mntpt + "/") or (path.startswith(mntpt) and mntpt.endswith("/")) or path == mntpt:
    	    #JSH:reparsing for get loop mounted url
    	    if path[len(mntpt):].__contains__("media/kvcd/vcd") or i[0].__contains__("/dev/loop"):
    	    	path = os.popen('losetup -a').read()
    	    	p = path.split("(")[1].split(")")[0]
    	    	if len(p) > 62:
    		    msg = gtk.MessageDialog(None, gtk.DIALOG_MODAL,
    	    	    	gtk.MESSAGE_ERROR, gtk.BUTTONS_OK, _("Error is occured while preparing installation. seemed too long url seted install image path"))
		    msg.run()
    		    sys.exit(0)
		    
    	    	return geturl( p, 0 )
    	    return ( mntpt, path[len(mntpt):], i[0])
    return (None, None, None)
    
def getmethodstr(path):
    url = geturl(path, 0)
    
    if url[0] == None and url[1] == None:
    	return None
    
    if url[1].__contains__("media/kvcd/vcd") or url[2].__contains__("/dev/loop"):
    	path = os.popen('losetup -a').read()
    	p = path.split("(")[1].split(")")[0]
    	if len(p) > 62:
    	    msg = gtk.MessageDialog(None, gtk.DIALOG_MODAL,
    	    	    	gtk.MESSAGE_ERROR, gtk.BUTTONS_OK, _("Error is occured while preparing installation. seemed too long url seted install image path"))
	    msg.run()
    	    sys.exit(0)
    #JSH: by now, we don't need using of ~rspath anymore
    """
    	url = geturl(p, 0)
    		
    file = open(url[0] + "/~rspath.dat", "w")
    file.write(url[1])
    file.close()
    """
    if url[1].startswith("/"):
    	return "hd:%s:%s" % (url[0][5:], url[1])
    return "hd:%s:/%s" % (url[0][5:], url[1])
    
def makeGrub(path, args, method):
    os.system('grubby --remove-kernel=/boot/rs3.0/vmlinuz')
    os.system('cp /boot/grub/grub.conf /boot/grub/grub.conf.rs3.0')
    getmethodstr(path)
    (mntpt, path, dev) = geturl(path, 0)
    #JSH: uuid means UUID of partition holding installation data...
    
    # 1: try using blkid
    uuid = ""
    if dev:
    	buf = os.popen("blkid -s UUID %s" % dev).read()
    	uuidpos = buf.find("UUID=")
    	if uuidpos >=0:
    	    uuid = buf[uuidpos + 5:].strip()
    	    if uuid.startswith('"'):
    		uuid = uuid[1:]
    	    if uuid.endswith('"'):
    		uuid = uuid[:-1]
    	
    	#2: try using lshal
    	#if uuid == "":
    	#    _part = "'%s'" % dev
    	#    lshal = os.popen("lshal").read().split("\n\n")
    	#    for _dev in lshal:
    	#    	if _part in _dev:
    	#    	    uuid = \
    	#    	    	_dev.split("\n")[0]\
    	#    	    	.split("volume_uuid_")[1]\
    	#    	    	.replace("_", "-")\
    	#	    	.replace("'", "" )
	    
        if uuid != "":
    	    uuid = "uuid=" + uuid
    	else:
    	    uuid = "instdev=" + dev
    
    
#/JSH: 	for prevent bug occured by grub.conf and insert of timeline : 2010.04.01
#	If grub.conf has no root_ID install can't initialize because grubby using this one
    arg = ""
    pre_line = ""
    buf = ""
    
    #JSH: add into grub "vga=0x317" option for bootsplash on device has no fb
    f = open ("/proc/fb", "r")    
    has_fb = 0
    if f:
    	has_fb = f.read().replace(" ","").__len__()    
    	f.close()    
    
    try:
        version = "%s%s" % ( open( "%s/.discinfo" % constants.realpath, "r" ).read().split("\n")[1], _(" Setup"))
    except:
        version = _("RedStar3.0_Install")
    
    version = version.replace(" ", "\ ")
    
    if not has_fb:    
        fb = "vga=0x317"
    else:
    	fb = ""
    rc = os.system('grubby --copy-default --make-default --add-kernel=/boot/rs3.0/vmlinuz --initrd=/boot/rs3.0/initrd.img \
    	--title=%s --args="selinux=1 lang=ko keymap=us bootpart=%s bootconfpath=%s %s setupmedia=%s %s \
    	quiet %s RS3URL=%s"' \
    	% ( version, geturl("/boot/grub/grub.conf", 0)[0],geturl("/boot/grub/grub.conf", 0)[1], args, method, uuid, fb, path))
    	
    if not rc == 0:
    	#print "grub has no arg..."
    	(_mntpt, _path, _dev) = geturl("/", 0)
    	#JSH: _uuid means UUID of current partition
    	
    	# 1: try using blkid
    	_uuid = ""
    	if _dev:
    	    buf = os.popen("blkid -s UUID %s" % _dev).read()
    	    uuidpos = buf.find("UUID=")
    	    if uuidpos >=0:
    	    	_uuid = buf[uuidpos + 5:].strip()
    	    	if _uuid.startswith('"'):
    	    	    _uuid = _uuid[1:]
    	    	if _uuid.endswith('"'):
    	    	    _uuid = _uuid[:-1]
	
	#2: try using lshal
	#if _uuid == "":
	#    _part = "'%s'" % dev
	#    lshal = os.popen("lshal").read().split("\n\n")
	#    for _dev in lshal:
	#    	if _part in _dev:
	#    	    _uuid = \
	#    	    	_dev.split("\n")[0]\
	#    	    	.split("volume_uuid_")[1]\
	#    	    	.replace("_", "-")\
	#	    	.replace("'", "" )
    	    
    	rc = os.system('grubby --copy-default --make-default --add-kernel=/boot/rs3.0/vmlinuz --initrd=/boot/rs3.0/initrd.img \
    	    --title=%s --args="selinux=1 lang=ko keymap=us bootpart=%s bootconfpath=%s %s setupmedia=%s %s \
    	    ro root=UUID=%s quiet %s RS3URL=%s"' \
    	    % ( version, geturl("/boot/grub/grub.conf", 0)[0],geturl("/boot/grub/grub.conf", 0)[1], args, method, uuid, _uuid, fb, path))
    try:
    	file = open("/boot/grub/grub.conf", "r")
    	buf = file.read().split("\n")
    	file.close()
    		
    	file = open("/boot/grub/grub.conf", "w+")
    	for i in buf:
    	    if path.__contains__(" "):    
    	    	if i.strip().__contains__("RS3URL="):
    	    	    i = i.split("RS3URL=")[0] + "RS3URL=" + path.replace(" ", "\ ")
    	    if i.__contains__("timeout"):
    	    	i = "timeout=3"
    	    file.write("%s\n" % i)
    	file.close()    
    except:
    	print "error occured while editing grub.conf"			
    
    return rc

def install(path, args, method):
    blpath = "/boot/rs3.0"
    try:
	os.makedirs(blpath)
    except:
	pass
    #if dmidecode.dmidecode() == "Apple Inc.":
    if bios.isMac(bios):
    	rc = os.system("cp %s/isolinux/vmlinuz_mac %s/vmlinuz" % (path, blpath))
    	if rc:
    	    return -1
    	rc = os.system("cp %s/isolinux/initrd_mac.img %s/initrd.img" % (path, blpath))
    	rc = os.system("cp %s/isolinux/initrd_mac.img %s/initrd.img" % (path, blpath))
    else:
    	rc = os.system('cp -f "%s/isolinux/vmlinuz" "%s/isolinux/initrd.img" %s' % (path, path, blpath))
    if rc:
        return -1
    if makeGrub(path, args, method):
    	return -1
    return 0

#print install("/media/isoFiles/media_LDATA2_GenRelease_Products_redstar_desktop_iso/", "")
