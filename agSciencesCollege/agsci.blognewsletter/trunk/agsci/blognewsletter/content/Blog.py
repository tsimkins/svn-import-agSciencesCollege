from AccessControl import ClassSecurityInfo
from Products.Archetypes.atapi import *
from Products.Archetypes.public import LinesField, LinesWidget
from zope.interface import implements

from Products.ATContentTypes.content.folder import ATFolder
from Products.ATContentTypes.content.schemata import ATContentTypeSchema, finalizeATCTSchema

from agsci.blognewsletter.content.interfaces import IBlog
from agsci.blognewsletter.config import *

Blog_schema = getattr(ATFolder, 'schema', Schema(())).copy() + Schema((

        LinesField(
            "available_public_tags",
            required=False,
            widget = LinesWidget(
                label=u"Available public tags",
                description=u"Add the tags that will be available for contributors to this blog.",
            ),

        ),

))

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
