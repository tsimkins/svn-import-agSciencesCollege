__author__ = """WebLion"""
__docformat__ = 'plaintext'

from AccessControl import ClassSecurityInfo
from Products.Archetypes.atapi import *
from zope.interface import implements

from Products.ATContentTypes.content.folder import ATFolder
from Products.ATContentTypes.configuration import zconf
from Products.ATContentTypes.content.schemata import ATContentTypeSchema, finalizeATCTSchema

from plone.app.layout.navigation.interfaces import INavigationRoot

from Products.CMFCore.permissions import View

from agsci.subsite.content.interfaces import ISubsite
from agsci.subsite.config import *

from Products.CMFCore import permissions

Subsite_schema = getattr(ATFolder, 'schema', Schema(())).copy() 

finalizeATCTSchema(Subsite_schema, folderish=True)

class Subsite(ATFolder):
    """
    """
    security = ClassSecurityInfo()
    implements(ISubsite)
    
    portal_type = 'Subsite'
    _at_rename_after_creation = True
    
    schema = Subsite_schema
    

registerType(Subsite, PROJECTNAME)
