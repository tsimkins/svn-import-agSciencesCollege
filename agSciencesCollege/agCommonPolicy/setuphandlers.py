# Create new members with properties supplied from a CSV file.
# The script expects a File object with id `users.csv` in the same folder
# it resides.
#
# The format of the CSV needs to be:
#
# password;userid;lastname;firstname;email
#
# created 2006-11-03 by Tom Lazar <tom@tomster.org>, http://tomster.org/
# under a BSD-style licence (i.e. use as you wish but don't sue me)

from zope.component import getSiteManager
from Products.CMFCore.utils import getToolByName
import string
import random

random.seed()

def createUsers(context):

	site = context.getSite()

	users = [
				["trs22", "Simkins", "Tim", "trs22@psu.edu"],
				["cjm49", "More", "Chris", "cjm49@psu.edu"],
				["aln", "Nakpil", "Albert", "aln@psu.edu"],
				["axd159", "Devlin", "Ann", "axd159@psu.edu"],
				["mjw174", "Wodecki", "Mary", "mjw174@psu.edu"],
				["pgw105", "Warren", "Pete", "pgw105@psu.edu"],
				["tds194", "Sassman", "Tyler", "tds194@psu.edu"]
			]

	printed = []
	sm = getSiteManager(site)
	regtool = getToolByName(sm, 'portal_registration')
	grouptool = getToolByName(sm, 'portal_groups')
	
	administratorsGroup = grouptool.getGroupById("Administrators")
	
	index = 1
	imported_count = 0
	
	for tokens in users:
	
		if len(tokens) == 4:
			id, last, first, email = tokens
			properties = {
				'username' : id,
				'fullname' : '%s %s' % (first, last),
				'email' : email.strip(),
			}
			try:
				regtool.addMember(id, randomPassword(), properties=properties)
				printed.append("Successfully added %s %s (%s) with email %s" % (first, last, id, email))
				imported_count += 1
				
			except ValueError, e:
				printed.append("Couldn't add %s: %s" % (id, e))
	
	
			try:
			
				administratorsGroup.addMember(id) 
				printed.append("Successfully added %s to Administrators group" % (id))
				
			except:
	
				printed.append("Couldn't add %s to Administrators group" % (id))
	
		else:
			printed.append("Could not parse line %d because it had the following contents: '%s'" % (index, user))
		index += 1
	
	printed.append("Imported %d users (from %d total users)" % (imported_count, index))
	
	return "\n".join(printed)

def randomPassword():
	d = [random.choice(string.letters) for x in xrange(32)]
	s = "".join(d)
	return s

def deleteUnusedFolders(context):
	site = context.getSite()
	for theFolder in ['Members', 'news', 'events']:
		if theFolder in site.objectIds():
			urltool = getToolByName(site, "portal_url")
			portal = urltool.getPortalObject()
			portal.manage_delObjects([theFolder])
			print "deleted folder %s" % theFolder
		else:
			print "Folder %s not found" % theFolder
			

def createSiteFolders(context):
	site = context.getSite()
	# Publish from http://svn.cosl.usu.edu/svndev/eduCommons3/branches/yale-3.0.2/setupHandlers.py
	wftool =  getToolByName(site, 'portal_workflow')

	for theArray in [['about', 'About Us'], ['news', 'News'], ['events', 'Events'], ['contact', 'Contact Us']]:
		(theId, theTitle) = theArray
		
		if theId not in site.objectIds():
			site.invokeFactory('Folder', id=theId, title=theTitle)
			
			theObject = getattr(site, theId)
			
			if wftool.getInfoFor(theObject, 'review_state') != 'Published':
				wftool.doActionFor(theObject, 'publish')

			print "Created and published folder %s" % theId
		else:
			print "Whoops, %s already exists" % theId
			
def configureFrontPage(context):
	site = context.getSite()

	if hasattr(site, 'front-page'):
		frontPage = getattr(site, 'front-page')
		frontPage.setText('Home Page should be set to "Homepage View"')
		frontPage.setTitle('Home')
		frontPage.setDescription('')
		frontPage.setPresentation(False)
		
def setSitePortlets(context):

	site = context.getSite()
	
	leftColumn = getUtility(IPortletManager, name=u'plone.leftcolumn', context=site)
	left = getMultiAdapter((portal, leftColumn), IPortletAssignmentMapping, context=site)
	
	rightColumn = getUtility(IPortletManager, name=u'plone.rightcolumn', context=portal)
	right = getMultiAdapter((portal, rightColumn), IPortletAssignmentMapping, context=portal)

	# Turn off right hand portlets
	if u'review' in right:
		del right[u'review']
	
	if u'news' in right:
		del right[u'news']
	
	if u'events' in right:
		del right[u'events']
	
	if u'calendar' in right:
		del right[u'calendar']

def setupHandlersWrapper(context):
	
	site = context.getSite()
	
	createUsers(context)
	
	deleteUnusedFolders(context)
	
	createSiteFolders(context)

	configureFrontPage(context)

	
			

	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
