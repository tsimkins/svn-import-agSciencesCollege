from AccessControl import ClassSecurityInfo
from Products.Archetypes.atapi import *
from zope.interface import implements

from Products.ATContentTypes.content.folder import ATFolder
from Products.ATContentTypes.content.schemata import ATContentTypeSchema, finalizeATCTSchema

from pugdemo.subsite.content.interfaces import ISubsite
from pugdemo.subsite.config import *

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
