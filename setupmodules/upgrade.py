#!/usr/bin/python

import os
import rpm
import constants
import time
import install

#for processing korean...
from rhpl.translate import _, textdomain, addPoPath

hdlistPath = "/RedStar/base/hdlist"
removeNames = ["arpro", "device-manager"]

def getUpgradable():
    upgradables = []
    
    if not constants.hdlist:
	fn = constants.getFilename("RedStar/base/hdlist")
	print fn
	hdlist = rpm.readHeaderListFromFile(fn)
	constants.hdlist = hdlist
    else:
	hdlist = constants.hdlist

    if not constants.ts:
	ts = rpm.TransactionSet()
	constants.ts = ts
    else:
	ts = constants.ts

    for hdr in hdlist:
	if hdr['n'].startswith('glibc'):
	    continue
	if hdr['n'].find('font') >= 0:
	    continue
	if hdr['n'].find('xfs') >= 0:
	    continue

	mi = ts.dbMatch(rpm.RPMTAG_NAME, hdr['n'])
	isInstalled = False
	existsOld = False

	for i in mi:
	    isInstalled = True
	    if hdr['v'] == i['v'] and hdr['r'] == i['r'] and hdr['buildtime'] == i['buildtime']:
		existsOld = False
		break

	    cr = rpm.versionCompare(hdr, i)
	    if cr > 0:
		existsOld = True
	    elif hdr['r'] == i['r'] + '.rs1.1':
		existsOld = True
	    elif hdr['buildtime'] > i['buildtime']:
		existsOld = True
	    elif cr <=0:
		existsOld = False
		break

	if isInstalled and existsOld:
	    upgradables.append(hdr)
	elif not isInstalled:
	    upgradables.append(hdr)
    constants.upgradables = upgradables
    return upgradables

def buildProvDict(hdrList):
    if constants.provDict:
	return
    print "Building dictionary"

    dict = {}
    for hdr in hdrList:
	for i in hdr['provides']:
	    dict[i] = hdr
	for i in hdr['filenames']:
	    dict[i] = hdr

    constants.provDict = dict
    print "Building dictionary done"

def processDep(hdrList):
    oldDeps = []
    provDict = None
    ts = constants.ts

    while 1:
	deps = ts.check()
	if oldDeps == deps:
	    break

	buildProvDict(hdrList)

	for i in deps:
	    if constants.provDict.has_key(i[1][0]):
		ts.addInstall(constants.provDict[i[1][0]], constants.provDict[i[1][0]], "i")
		print "added by dependencies:%s" % constants.provDict[i[1][0]]['name']

	oldDeps = deps

def upgrade(cbfunc, textfunc, upgradeList, hdrList):

    if not constants.ts:
	ts = rpm.TransactionSet()
	constants.ts = ts
    else:
	ts = constants.ts
    ts.clean()
    ts.setFlags(rpm.RPMTRANS_FLAG_NOCONFIGS)
    ts.setVSFlags(~(rpm.RPMVSF_NORSA|rpm.RPMVSF_NODSA))

    for i in removeNames:
	mi = ts.dbMatch(rpm.RPMTAG_NAME, i)
	if mi.count() > 0:
	    ts.addErase(i)

    for i in upgradeList:
	mi = ts.dbMatch(rpm.RPMTAG_NAME, i['n'])
	if mi.count() > 0:
	    ts.addErase(i['n'])
	ts.addInstall(i, i, "i")

    processDep(hdrList)
    ts.setProbFilter(~rpm.RPMPROB_FILTER_DISKSPACE)

    installedPkgs = ts.getKeys()
    constants.totalsize = 0

    for i in installedPkgs:
	if i:
	    constants.totalsize += i[rpm.RPMTAG_ARCHIVESIZE]

    print "totalSize:", constants.totalsize

    ts.order()
    err = ts.run(cbfunc, textfunc)
    os.system("sed -i 's/id:3/id:5/g' /etc/inittab")
    os.system("sed -i 's, (2.6.18-1.2798.rs1.1),,g' /boot/grub/grub.conf")
    return err

def upgradeDaemon():
    daemonfile = "/etc/rc.d/rc5.d/S00upgradedaemon"
    mountpoint = "/tmp/hdimage"
    try:
    	os.system("rm -rf /tmp/rssetup")
        os.system("mkdir -p /tmp/rssetup")
        os.system("cp %s/autorun /tmp/rssetup" % constants.realpath)
        os.system("cp %s/setdata /tmp/rssetup" % constants.realpath)
        os.system("cp %s/install /tmp/rssetup" % constants.realpath)
        if os.access("%s/.discinfo" % constants.realpath, os.R_OK):
    	    os.system("cp %s/.discinfo /tmp/rssetup" % constants.realpath)
        os.system("cp -R %s/setupmodules /tmp/rssetup" % constants.realpath)
        os.system("mkdir -p /etc/yum.repos.d")
        os.system("cat %s/setupmodules/repos/redstar-core.repo > /etc/yum.repos.d/redstar-core.repo" % constants.realpath)
        os.system("cat %s/setupmodules/repos/onlineupdate.repo > /etc/yum.repos.d/onlineupdate.repo" % constants.realpath)
    except:
	print "error on copying setupmodules..."
	
    try:
	url = install.geturl(constants.realpath, 0)
	file = open(daemonfile, "w")
	file.write("#!/bin/sh\n")
	file.write("rm -f %s\n" % daemonfile)
	file.write("mkdir -p %s\n" % mountpoint)
	file.write('export PRODDEV="%s"\n' % url[0])
	file.write('export PRODPATH="%s"\n' % url[1])
	file.write('service xfs restart\n')
	file.write('/usr/bin/xinit /tmp/rssetup/install\n')
	file.write('service xfs stop\n')
	file.write("rmdir %s\n" % mountpoint)
	file.write("reboot\n")
	file.close()
	os.system("chmod 755 %s" % daemonfile)
	os.system("umount %s" % url[0])
	os.system("umount -l %s" % url[0])
	os.system("eject %s" % url[0])
    except:
	return 1
    return 0
