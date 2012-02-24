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

from agsci.subsite.content.interfaces import IPhotoFolder
from agsci.subsite.config import *

from Products.CMFCore import permissions

PhotoFolder_schema = getattr(ATFolder, 'schema', Schema(())).copy() 

finalizeATCTSchema(PhotoFolder_schema, folderish=True)

class PhotoFolder(ATFolder):
    """
    """
    security = ClassSecurityInfo()
    implements(IPhotoFolder)
    
    portal_type = 'PhotoFolder'
    _at_rename_after_creation = True
    
    schema = PhotoFolder_schema
    

registerType(PhotoFolder, PROJECTNAME)
