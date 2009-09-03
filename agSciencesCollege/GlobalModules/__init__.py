from Products.PythonScripts.Utility import allow_module
allow_module('feedparser')
allow_module('datetime')
allow_module('datetime.datetime')
allow_module('Products.feedSync')
allow_module('Products.feedSync.sync')
allow_module('Products.CMFCore.utils')
allow_module('Products.CMFCore.utils.getToolByName')
allow_module('zope.component')
allow_module('zope.component.getSiteManager')

allow_module('Products.GlobalModules')
allow_module('Products.GlobalModules.makeHomePage')

def makeHomePage(context):
    print context.portal_type
    print context.archetype_name
    context.archetype_name = 'Home Page'
    context.portal_type = 'HomePage'
    context.reindexObject()
    print context.portal_type
    print context.archetype_name
    print "OK"
