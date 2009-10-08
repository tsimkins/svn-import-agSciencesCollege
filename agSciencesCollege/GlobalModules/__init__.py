from Products.PythonScripts.Utility import allow_module
import re

allow_module('feedparser')
allow_module('datetime')
allow_module('datetime.datetime')
allow_module('Products.feedSync')
allow_module('Products.feedSync.sync')
allow_module('Products.feedSync.cvent')
allow_module('Products.feedSync.cvent.importEvents')
allow_module('Products.CMFCore.utils')
allow_module('Products.CMFCore.utils.getToolByName')
allow_module('zope.component')
allow_module('zope.component.getSiteManager')

allow_module('Products.GlobalModules')
allow_module('Products.GlobalModules.makeHomePage')
allow_module('Products.GlobalModules.makePhotoFolder')
allow_module('Products.GlobalModules.fixPhoneNumber')

allow_module('ZODB.POSException')
allow_module('ZODB.POSException.POSKeyError')

allow_module('re')
allow_module('re.sub')
allow_module('re.compile')

phoneRegex = re.compile(r"^\((\d{3})\)\s+(\d{3})\-(\d{4})$")

def makeHomePage(context):
    print context.portal_type
    print context.archetype_name
    context.archetype_name = 'Home Page'
    context.portal_type = 'HomePage'
    context.reindexObject()
    print context.portal_type
    print context.archetype_name
    print "OK"

def makePhotoFolder(context):
    print context.portal_type
    print context.archetype_name
    context.archetype_name = 'Photo Folder'
    context.portal_type = 'PhotoFolder'
    context.reindexObject()
    print context.portal_type
    print context.archetype_name
    print "OK"

def fixPhoneNumber(myPerson):

    phone = myPerson.getOfficePhone()
    newPhone = phoneRegex.sub(r"\1-\2-\3", phone)

    if newPhone != phone:
        myPerson.setOfficePhone(newPhone)
        myPerson.reindexObject()
        return "%s: from %s to %s" % (myPerson.id, phone, newPhone)
    else:
        return "%s: Phone OK" % myPerson.id

