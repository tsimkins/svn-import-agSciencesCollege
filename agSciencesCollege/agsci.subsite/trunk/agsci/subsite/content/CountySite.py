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

from agsci.subsite.content.interfaces import ICountySite
from agsci.subsite.config import *

from Products.CMFCore import permissions

CountySite_schema = getattr(ATFolder, 'schema', Schema(())).copy() 

finalizeATCTSchema(CountySite_schema, folderish=True)

class CountySite(ATFolder):
    """
    """
    security = ClassSecurityInfo()
    implements(ICountySite)
    
    portal_type = 'CountySite'
    _at_rename_after_creation = True
    
    schema = CountySite_schema
    

registerType(CountySite, PROJECTNAME)
