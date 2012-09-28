from Products.CMFCore.utils import getToolByName
from Products.PythonScripts.Utility import allow_module
from zope.i18nmessageid import MessageFactory
from DateTime import DateTime

seoMessageFactory = MessageFactory('agsci.seo')

allow_module('agsci.seo')

def initialize(context):
    pass


def getDisallowedPaths(context):
    
    now = DateTime()
    
    portal_catalog = getToolByName(context, 'portal_catalog')

    results = [x for x in portal_catalog.searchResults({'exclude_from_robots' : True})]
    results.extend([x for x in portal_catalog.searchResults({'portal_type' : 'Event', 'end' : {'query' : now, 'range' : 'max'}})])
    results.extend([x for x in portal_catalog.searchResults({'expires' : {'query' : now, 'range' : 'max'}})])
    
    portal_url = context.portal_url()
    
    disallow = []
    
    for r in results:
        disallow.append(r.getURL().replace(portal_url, '') )
    
    return sorted(list(set(disallow)))
