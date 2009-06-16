#!/usr/bin/python

import re

ploneObjects = {}

#Ploneify
def ploneify(toPlone):
	ploneString = re.sub("[^A-Za-z0-9]+", "-", toPlone).lower()
	ploneString = re.sub("-$", "", ploneString)
	ploneString = re.sub("^-", "", ploneString)
	
	serial = ploneObjects.get(ploneString, None)
	
	if serial:
		ploneObjects[ploneString] = serial + 1
		return ploneString + "-" + str(serial)
	else:
		ploneObjects[ploneString] = 1
		return ploneString

def comment(text):
		
	print "#" + "-"*60
	print "# %s" % str(text)
	print "#" + "-"*60
	
def getFlags(flags):
	myFlags = {}
	for f in [x.strip().lower() for x in flags.split(',')]:
		if f.count('=') > 0:
			(myKey, myValue) = [x.strip() for x in f.split('=')]
			myFlags[myKey] = myValue
		elif f != "":
			myFlags[f] = True

	return myFlags

def excludeFromNav(id):

	comment("Hiding %s from navigation" % id)

	print """

myObject = getattr(myContext, "%(id)s")
myObject.setExcludeFromNav(True)
myObject.reindexObject()

""" % { "id" : id }

def setContext(url):

	if url.startswith("/"):
		url = url.replace("/", "", 1)
	
	print "myContext = context\n"

	urlArray = [x.strip() for x in url.split("/")]
	urlArray.pop()

	for fragment in urlArray:
		print "myContext = getattr(myContext, '%s')\n" % fragment


def publish(id):
	print """
myObject = getattr(myContext, '%(id)s')

if wftool.getInfoFor(myObject, 'review_state') != 'published':
    wftool.doActionFor(myObject, 'publish')
""" % {"id" : id} 

def setAsDefault(id):
	print """myContext.setDefaultPage('%(id)s')""" % {"id" : id} 

def importModules():

	# This prints the import for the necessary modules when the package is imported
	
	print """
from zope.component import getSiteManager
from Products.CMFCore.utils import getToolByName

import transaction

from Testing.makerequest import makerequest

from AccessControl.SecurityManagement import newSecurityManager
"""


def setLocation(site, url):
	print """
app = makerequest(app)
mySite = getattr(app, '%s')
""" % site

	if url.startswith("/"):
		url = url.replace("/", "", 1)
	
	print "context = mySite\n"

	urlArray = [x.strip() for x in url.split("/")]

	for fragment in urlArray:
		print "context = getattr(context, '%s')\n" % fragment

	print """
admin = app.acl_users.getUserById('admin')
admin = admin.__of__(app.acl_users)
newSecurityManager(None, admin) 

portal = getSiteManager(context)
wftool = getToolByName(portal, "portal_workflow")
"""

def commit():
	print """
transaction.commit()
"""

# We'll need the import modules anyway
importModules()
