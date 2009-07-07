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

from zope.component import getSiteManager, getUtility, getMultiAdapter
from zope.component.interfaces import ComponentLookupError
from Products.CMFCore.utils import getToolByName
from plone.portlets.interfaces import IPortletManager, IPortletAssignmentMapping
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

			theFolderObject = getattr(site, theFolder)
			if theFolderObject.getPortalTypeName() != 'Folder':			
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

	for theArray in [['about', 'About Us'], ['news', 'News'], ['events', 'Events'], ['contact', 'Contact Us'], ['background-images', 'Background Images']]:
		(theId, theTitle) = theArray
		
		if theId not in site.objectIds():
			site.invokeFactory('Folder', id=theId, title=theTitle)
			
			theObject = getattr(site, theId)
			
			if wftool.getInfoFor(theObject, 'review_state') != 'Published':
				wftool.doActionFor(theObject, 'publish')

			if theId == 'background-images':
				theObject.setExcludeFromNav(True)
				theObject.reindexObject()

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
		frontPage.setLayout("document_homepage_view")

		
def setSitePortlets(context):

	site = context.getSite()

	print "Setting site portlets."

	try:

		ploneLeftColumn = getUtility(IPortletManager, name=u'plone.leftcolumn', context=site)
		ploneLeft = getMultiAdapter((site, ploneLeftColumn), IPortletAssignmentMapping, context=site)

		ploneRightColumn = getUtility(IPortletManager, name=u'plone.rightcolumn', context=site)
		ploneRight = getMultiAdapter((site, ploneRightColumn), IPortletAssignmentMapping, context=site)
	
	except ComponentLookupError:
		print "ComponentLookupError"

	else:

		for deletePortlet in [u'review', u'news', u'events', u'calendar']:
			try:
				del ploneRight[deletePortlet]
				print "Deleted %s" % deletePortlet
			except KeyError:
				print "No portlet named %s" % deletePortlet
			
			
		for deletePortlet in [u'login']:
			try:
				del ploneLeft[deletePortlet]
				print "Deleted %s" % deletePortlet
			except KeyError:
				print "No portlet named %s" % deletePortlet

		if ploneLeft.has_key('navigation'):
			print "Set navigation portlet start level"
			ploneLeft['navigation'].topLevel = 0


def addExtensionToMimeType(registry, extension, mimetype):
	for myMime in registry.lookup(mimetype):
		glob = '*.%s' % extension
		registry.register_extension(extension, myMime)
		registry.register_glob(glob, myMime)

		newExtensions = list(myMime.extensions)
		newExtensions.append(extension)
		newExtensions = tuple(newExtensions)

		newGlobs = list(myMime.globs)
		newGlobs.append(glob)
		newGlobs = tuple(newGlobs)

		myMime.edit(myMime.name(), myMime.mimetypes, newExtensions, myMime.icon_path, globs=newGlobs)

		print "Added extension %s to mimetype %s" % (extension, mimetype)

def configureMimeTypes(context):
	
	site = context.getSite()
	
	listOfMimeTypes = [
			['docm', 'application/msword'],
			['docx', 'application/msword'],
			['dotm', 'application/msword'],
			['dotx', 'application/msword'],
			['potm', 'application/vnd.ms-powerpoint'],
			['potx', 'application/vnd.ms-powerpoint'],
			['ppam', 'application/vnd.ms-powerpoint'],
			['ppsm', 'application/vnd.ms-powerpoint'],
			['ppsx', 'application/vnd.ms-powerpoint'],
			['pptm', 'application/vnd.ms-powerpoint'],
			['pptx', 'application/vnd.ms-powerpoint'],
			['xlam', 'application/vnd.ms-excel'],
			['xlsb', 'application/vnd.ms-excel'],
			['xlsm', 'application/vnd.ms-excel'],
			['xlsx', 'application/vnd.ms-excel'],
			['xltm', 'application/vnd.ms-excel'],
			['xltx', 'application/vnd.ms-excel']
	]

	mimetypes_registry = getattr(site, 'mimetypes_registry')

	for (extension, mimetype) in listOfMimeTypes:
		 addExtensionToMimeType(mimetypes_registry, extension, mimetype)


def setupHandlersWrapper(context):
	
	site = context.getSite()
	
	createUsers(context)
	
	deleteUnusedFolders(context)
	
	createSiteFolders(context)

	configureFrontPage(context)
	
	setSitePortlets(context)

	configureMimeTypes(context)

	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
