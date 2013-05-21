from zope.i18nmessageid import MessageFactory
ExtensionExtenderMessageFactory = MessageFactory('agsci.ExtensionExtender')
from Products.CMFCore.utils import getToolByName
from Products.PythonScripts.Utility import allow_module
from Products.Five.utilities.interfaces import IMarkerInterfaces
from agsci.ExtensionExtender.interfaces import IExtensionPublicationExtender, IExtensionCountiesExtender

from Products.CMFCore import DirectoryView

# Register our skins directory - this makes it available via portal_skins.

DirectoryView.registerDirectory('skins', globals())

allow_module('agsci.ExtensionExtender')

def initialize(context):
    pass

def getContactEmails(context, county=None, program=None, topic=None, subtopic=None):
    portal_catalog = getToolByName(context, "portal_catalog")

    query = {'portal_type' : 'FSDPerson'}
    emails = []
    
    if county:
        query['Counties'] = county

    if topic:
        query['Topics'] = topic

    if subtopic:
        query['Subtopics'] = subtopic

    if program:
        query['Programs'] = program

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
    attrs = {'county' : 'extension_counties', 'program' : 'extension_programs', 'topic' : 'extension_topics', 'subtopic' : 'extension_subtopics'}
    for k in attrs.keys():
        v = attrs[k]
        config[k] = []
        if hasattr(context, v):
            val = getattr(context, v)
            if val:
                config[k] = list(val)
    return config

def enablePublication(context):
    if not IExtensionPublicationExtender.providedBy(context):
        adapted = IMarkerInterfaces(context)
        adapted.update(add=[IExtensionPublicationExtender])
        return True
    else:
        return False
    
def enableCounties(context):
    if not IExtensionCountiesExtender.providedBy(context):
        adapted = IMarkerInterfaces(context)
        adapted.update(add=[IExtensionCountiesExtender])
        return True
    else:
        return False