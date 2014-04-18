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

# Monkey patch collection criteria
from Products.Archetypes.atapi import IntDisplayList
from Products.ATContentTypes.criteria.date import ATDateCriteriaSchema as _ATDateCriteriaSchema
from Products.ATContentTypes.criteria import date
from Products.ATContentTypes import ATCTMessageFactory as _

DateOptions = IntDisplayList((
                (     0, _(u'Now')      )
                , (     1, _(u'1 Day')    )     
                , (     2, _(u'2 Days')   )    
                , (     5, _(u'5 Days')   )
                , (     7, _(u'1 Week')   )    
                , (    14, _(u'2 Weeks')  )       
                , (    21, _(u'3 Weeks')  )     
                , (    31, _(u'1 Month')  )
                , (  31*3, _(u'3 Months') )
                , (  31*6, _(u'6 Months') )
                , (   365, _(u'1 Year')   )
                , ( 365*2, _(u'2 Years')  )
))

_ATDateCriteriaSchema['value'].vocabulary = DateOptions

date.ATDateCriteriaSchema = _ATDateCriteriaSchema

logging.getLogger('agsci.UniversalExtender').info("Products.ATContentTypes.criteria.date.ATDateCriteriaSchema")