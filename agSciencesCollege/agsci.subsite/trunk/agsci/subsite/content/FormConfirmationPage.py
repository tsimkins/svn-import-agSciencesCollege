__author__ = """WebLion"""
__docformat__ = 'plaintext'

from AccessControl import ClassSecurityInfo
from Products.Archetypes.atapi import *
from zope.interface import implements

from Products.PloneFormGen.content.thanksPage import FormThanksPage
from Products.ATContentTypes.configuration import zconf
from Products.ATContentTypes.content.schemata import ATContentTypeSchema, finalizeATCTSchema

from plone.app.layout.navigation.interfaces import INavigationRoot

from Products.CMFCore.permissions import View

from agsci.subsite.config import *

from Products.CMFCore import permissions

from Products.PloneFormGen import PloneFormGenMessageFactory as _
from Products.PloneFormGen.interfaces import IPloneFormGenThanksPage
from Products.PloneFormGen.config import EDIT_TALES_PERMISSION, EDIT_ADVANCED_PERMISSION, BAD_IDS
from Products.Archetypes.interfaces.field import IField

FormConfirmationPage_schema = getattr(FormThanksPage, 'schema', Schema(())).copy() + Schema((

    StringField('formActionOverride',
        schemata='overrides',
        searchable=0,
        required=0,
        write_permission=EDIT_ADVANCED_PERMISSION,
        languageIndependent=1,
        widget=StringWidget(label=_(u'label_formactionoverride_text', default=u"Custom Form Action"),
            description=_(u'help_formactionoverride_text', default=u"""
                Use this field to override the form action attribute.
                Specify a URL to which the form will post.
                This will bypass form validation, success action
                adapter and thanks page.
            """),
            size=70,
            ),
        ),

    StringField('submitButtonText',
        schemata='overrides',
        searchable=0,
        required=0,
        write_permission=EDIT_ADVANCED_PERMISSION,
        languageIndependent=1,
        widget=StringWidget(label=_(u'label_formactionoverride_text', default=u"Submit Button Text"),
            description=_(u'help_formactionoverride_text', default=u"""
                Use this field to override the form submit button text
            """),
            size=70,
            ),
        ),

))

finalizeATCTSchema(FormConfirmationPage_schema, folderish=False)

class FormConfirmationPage(FormThanksPage):
    """
    """
    security = ClassSecurityInfo()
    implements(IPloneFormGenThanksPage)
    
    portal_type = 'FormConfirmationPage'
    _at_rename_after_creation = True
    
    schema = FormConfirmationPage_schema
    
    security.declareProtected(View, 'displayInputs')

    def hiddenFields(self, request):
        """ Returns sequence of dicts {'label':fieldlabel, 'value':input}
        """
        # get a list of all candidate fields
        myFields = []
        for obj in self.aq_parent._getFieldObjects():
            if not (IField.providedBy(obj) or obj.isLabel()):
                # if field list hasn't been specified explicitly, exclude server side fields
                if self.showAll and obj.getServerSide():
                    continue 
                myFields.append(obj)

        # Now, build the results list
        res = []
        for obj in myFields:
            value = obj.htmlValue(request)
            if self.includeEmpties or (value and (value != 'No Input')):
                res.append( {
                    'name' : obj.getId(),
                    'value' : value, 
                    } )
            
        return res


registerType(FormConfirmationPage, PROJECTNAME)
