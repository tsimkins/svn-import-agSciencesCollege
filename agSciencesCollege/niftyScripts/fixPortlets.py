# Copying portlets from plone right column to ag right column

from Products.CMFCore.utils import getToolByName
from zope.component import getUtility
from plone.portlets.interfaces import IPortletManager, IPortletAssignmentMapping
from zope.component import getMultiAdapter
from AccessControl.SecurityManagement import newSecurityManager
from zope.component.interfaces import ComponentLookupError
import transaction
	
def copyPortlets(myContext):

	try:

		ploneRightColumn = getUtility(IPortletManager, name=u'plone.rightcolumn', context=myContext)
		ploneRight = getMultiAdapter((myContext, ploneRightColumn), IPortletAssignmentMapping, context=myContext)
	
		agRightColumn = getUtility(IPortletManager, name=u'agcommon.rightcolumn', context=myContext)
		agRight = getMultiAdapter((myContext, agRightColumn), IPortletAssignmentMapping, context=myContext)
	
	except ComponentLookupError:
		print "ComponentLookupError"
	else:
		print ploneRight.keys()
	
		for assignment in ploneRight.keys():
			agRight[assignment] = ploneRight[assignment]
			print "copying %s" % assignment
			del ploneRight[assignment]
	
		transaction.commit()


def traverse(myContext):
	try:
		typeName = myContext.getPortalTypeName()
	except AttributeError:
		# apparently we don't have a portal type
		print "No portal type name"
	else:
        	if typeName != 'Image' and typeName != 'File':
	            #print "Processing %s" % myContext.get_absolute_url()
        	    copyPortlets(myContext)
    
        if typeName == 'Folder' or typeName == 'Plone Site':
		for myObject in myContext.listFolderContents():
			traverse(myObject)

admin = app.acl_users.getUserById('admin')
admin = admin.__of__(app.acl_users)
newSecurityManager(None, admin) 

agsci = getattr(app, 'das')
traverse(agsci)

transaction.commit()
