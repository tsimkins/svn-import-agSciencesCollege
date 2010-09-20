from zope.i18nmessageid import MessageFactory
UniversalExtenderMessageFactory = MessageFactory('agsci.UniversalExtender')
from Products.Archetypes.Schema import Schemata

def initialize(context):
    pass

def editableFields(self, instance, visible_only=False):
    """Returns a list of editable fields for the given instance
    """
    ret = []
    from Products.CMFCore.utils import getToolByName 
    portal = getToolByName(instance, 'portal_url').getPortalObject()
    for field in self.fields():
        if field.writeable(instance, debug=False) and    \
                (not visible_only or
                field.widget.isVisible(instance, 'edit') != 'invisible') and \
                field.widget.testCondition(instance.aq_parent, portal, instance):
            ret.append(field)

    return ret

Schemata.editableFields = editableFields

import logging
logging.getLogger('agsci.UniversalExtender').info("Monkey patched Products.Archetypes.Schema")