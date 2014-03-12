from zope.i18nmessageid import MessageFactory
from Products.CMFCore.utils import getToolByName
from Products.PythonScripts.Utility import allow_module
from Products.Five.utilities.interfaces import IMarkerInterfaces
from agsci.ExtensionExtender.interfaces import IExtensionCountiesExtender
from Products.CMFCore import DirectoryView

ExtensionExtenderMessageFactory = MessageFactory('agsci.ExtensionExtender')

# Register our skins directory - this makes it available via portal_skins.

DirectoryView.registerDirectory('skins', globals())

allow_module('agsci.ExtensionExtender')

def initialize(context):
    pass

def getContactEmails(context, county=None, topic=None, subtopic=None):
    portal_catalog = getToolByName(context, "portal_catalog")

    query = {'portal_type' : 'FSDPerson'}
    emails = []
    
    if county:
        query['Counties'] = county

    if topic:
        query['Topics'] = topic

    if subtopic:
        query['Subtopics'] = subtopic

    results = portal_catalog.searchResults(query)
    
    for r in results:
        e = r.getObject().getEmail()
        if e:
            emails.append(e)

    return emails

def getDefaultFormEmail(context):
    return context.getRawRecipient_email()

def getExtensionConfig(context):
    config = {}
    attrs = {'county' : 'extension_counties', 'topic' : 'extension_topics', 'subtopic' : 'extension_subtopics'}
    for k in attrs.keys():
        v = attrs[k]
        config[k] = []
        if hasattr(context, v):
            val = getattr(context, v)
            if val:
                config[k] = list(val)
    return config
    
def enableCounties(context):
    if not IExtensionCountiesExtender.providedBy(context):
        adapted = IMarkerInterfaces(context)
        adapted.update(add=[IExtensionCountiesExtender])
        return True
    else:
        return False

def pushNewsItemsToBlogs(context):
    order = [
        'news-food-safety',
    ]
    
    dest = {
        'news-food-safety' : {
                            'path' : '/food/safety/news',
                            'programs' : ['Food and Health:Food Safety', ]
        }
    }
    
    additional_tags = list(set(order) - set(dest.keys()))
    
    order.extend(additional_tags)
    
    portal_catalog = getToolByName(context, "portal_catalog")
    
    results = portal_catalog.searchResults({'portal_type' : 'News Item', 'Subject' : dest.keys(), 'path' : '/'.join(context.getPhysicalPath())})
    
    for r in results:
        o = r.getObject()
        o_subject = o.Subject()
        o_programs = list(o.extension_topics)
        new_destination = None
        for t in order:
            if t in o_subject:
                o_programs.extend(dest[t]['programs'])
                if not new_destination:
                    new_destination = dest[t]['path']
        o_programs = list(set(o_programs))
        o.extension_topics = o_programs
        o.reindexObject()
        new_parent = context.restrictedTraverse(new_destination.replace('/', '', 1))
        year = str(o.effective().year())
        if year in new_parent.objectIds():
            cb_copy_data = context.getParentNode().manage_cutObjects(ids=[o.getId()])
            new_parent[year].manage_pasteObjects(cb_copy_data=cb_copy_data)
    
    
                
                
                
            
    
    
    

    