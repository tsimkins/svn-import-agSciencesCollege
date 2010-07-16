'''Main product initializer'''

__author__ = """WebLion"""
__docformat__ = 'plaintext'

from Products.Archetypes import atapi
from Products.CMFCore import utils

from agsci.subsite.config import *

def initialize(context):
    """initialize product (called by zope)"""

    # import packages and types for registration
    # I really don't think I have to do these imports.
    from content import Subsite
    from content import Blog

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
