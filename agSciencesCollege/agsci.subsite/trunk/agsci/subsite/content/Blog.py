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

from agsci.subsite.content.interfaces import IBlog
from agsci.subsite.config import *

from Products.CMFCore import permissions

Blog_schema = getattr(ATFolder, 'schema', Schema(())).copy() 

finalizeATCTSchema(Blog_schema, folderish=True)

class Blog(ATFolder):
    """
    """
    security = ClassSecurityInfo()
    implements(IBlog)
    
    portal_type = 'Blog'
    _at_rename_after_creation = True
    
    schema = Blog_schema
    

registerType(Blog, PROJECTNAME)
