__author__ = """WebLion"""
__docformat__ = 'plaintext'

from AccessControl import ClassSecurityInfo
from Products.Archetypes.atapi import *
from zope.interface import implements

from Products.ATContentTypes.content.document import ATDocument
from Products.ATContentTypes.configuration import zconf
from Products.ATContentTypes.content.schemata import ATContentTypeSchema, finalizeATCTSchema

from plone.app.layout.navigation.interfaces import INavigationRoot

from Products.CMFCore.permissions import View

from agsci.subsite.content.interfaces import IHomePage
from agsci.subsite.config import *

from Products.CMFCore import permissions

HomePage_schema = getattr(ATDocument, 'schema', Schema(())).copy() 

finalizeATCTSchema(HomePage_schema, folderish=False)

class HomePage(ATDocument):
    """
    """
    security = ClassSecurityInfo()
    implements(IHomePage)
    
    portal_type = 'HomePage'
    _at_rename_after_creation = True
    
    schema = HomePage_schema
    

registerType(HomePage, PROJECTNAME)
