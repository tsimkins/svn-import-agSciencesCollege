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

from agsci.subsite.content.interfaces import ISection
from agsci.subsite.config import *

from Products.CMFCore import permissions

Section_schema = getattr(ATFolder, 'schema', Schema(())).copy() 

finalizeATCTSchema(Section_schema, folderish=True)

class Section(ATFolder):
    """
    """
    security = ClassSecurityInfo()
    implements(ISection)
    
    portal_type = 'Section'
    _at_rename_after_creation = True
    
    schema = Section_schema
    

registerType(Section, PROJECTNAME)
