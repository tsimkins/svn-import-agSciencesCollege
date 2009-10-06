# Copying portlets from ag right column to plone right column

from Products.CMFCore.utils import getToolByName
from zope.component import getUtility
from plone.portlets.interfaces import IPortletManager, IPortletAssignmentMapping
from zope.component import getMultiAdapter
from AccessControl.SecurityManagement import newSecurityManager
from zope.component.interfaces import ComponentLookupError
from ZODB.POSException import POSKeyError
import transaction
    
def copyPortlets(myContext):

    try:

        ploneRightColumn = getUtility(IPortletManager, name=u'plone.rightcolumn', context=myContext)
        ploneRight = getMultiAdapter((myContext, ploneRightColumn), IPortletAssignmentMapping, context=myContext)
    
        agRightColumn = getUtility(IPortletManager, name=u'agcommon.rightcolumn', context=myContext)
        agRight = getMultiAdapter((myContext, agRightColumn), IPortletAssignmentMapping, context=myContext)
    
    except ComponentLookupError:
        print "ComponentLookupError"
    except POSKeyError:
        print "POSKeyError"
    else:
        if agRight.keys():
            print agRight.keys()
    
            for assignment in agRight.keys():
                try:
                    ploneRight[assignment] = agRight[assignment]
                    print "copying %s" % assignment
                    del agRight[assignment]
                except KeyError:
                    print "KeyError"
      
            transaction.commit()


def traverse(myContext):
    try:
        typeName = myContext.getPortalTypeName()
        layout = myContext.getLayout()
    except AttributeError:
        # apparently we don't have a portal type
        print "No portal type name or layout: %s" % myContext
    else:
        if typeName != 'Image' and typeName != 'File' and typeName != 'HomePage' and layout != 'document_homepage_view':
            print "Processing %s, Type %s, Layout %s" % (myContext, typeName, layout)
            copyPortlets(myContext)

        if typeName != 'HomePage' and layout == 'document_homepage_view':
            try:
                print "HOMEPAGE WARNING: %s is Type %s, Layout %s" % (myContext.absolute_url(), typeName, layout)
            except AttributeError:
                print "BIG OOPS: %s is Type %s, Layout %s" % (myContext, typeName, layout)            
            
        if typeName == 'Folder' or typeName == 'Plone Site':
            for myObject in myContext.listFolderContents():
                traverse(myObject)

admin = app.acl_users.getUserById('admin')
admin = admin.__of__(app.acl_users)
newSecurityManager(None, admin) 

for site in ('4-h', 'agsci.psu.edu', 'courses', 'cropsoil.psu.edu', 'ento.psu.edu', 
				'extension.psu.edu', 'foodscience.psu.edu', 'graduatestudents', 
				'intranet-it', 'ipm', 'magazine', 'plone-test', 'sfr.psu.edu', 'thinkagain.psu.edu'):


	print "Doing %s" % site
	ploneSite = getattr(app, site)
	traverse(ploneSite)

transaction.commit()

