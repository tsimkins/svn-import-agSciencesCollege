from zope.i18nmessageid import MessageFactory
from Products.Archetypes import atapi
from Products.CMFCore import utils
from Products.CMFCore import DirectoryView

pugdemoMessageFactory = MessageFactory('pugdemo.subsite')

# Register our skins directory - this makes it available via portal_skins.
DirectoryView.registerDirectory('skins', globals())

from pugdemo.subsite.config import *

def initialize(context):
    """initialize product (called by zope)"""

    # import packages and types for registration
    from content import subsite

    content_types, constructors, ftis = atapi.process_types(
        atapi.listTypes(config.PROJECTNAME),
        config.PROJECTNAME)

    # Initialize the various content types
    for atype, constructor in zip(content_types, constructors):
        utils.ContentInit("%s: %s" % (config.PROJECTNAME, 
            atype.portal_type),
            content_types = (atype,),
            permission = config.ADD_PERMISSIONS[atype.portal_type],
            extra_constructors = (constructor,),
            ).initialize(context)
