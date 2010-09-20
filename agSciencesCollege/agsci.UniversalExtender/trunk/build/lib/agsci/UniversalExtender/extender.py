from Products.Archetypes.public import ImageField, ImageWidget, StringField, StringWidget
from Products.FacultyStaffDirectory.interfaces.person import IPerson
from Products.FacultyStaffDirectory.Person import IPerson
from archetypes.schemaextender.field import ExtensionField
from archetypes.schemaextender.interfaces import ISchemaExtender, ISchemaModifier, IBrowserLayerAwareExtender
from interfaces import IUniversalExtenderLayer
from zope.component import adapts
from zope.interface import implements

class _ExtensionStringField(ExtensionField, StringField): pass

class FSDPersonExtender(object):
    adapts(IPerson)
    implements(ISchemaExtender, ISchemaModifier, IBrowserLayerAwareExtender)

    layer = IUniversalExtenderLayer


    fields = [

        _ExtensionStringField(
            "fax",
            required=False,
            schemata="Contact Information",
            widget=StringWidget(
                label=u"Office Fax",
                description=u"Example: 555-1555-5555",
            ),
        ),
    ]

    def fiddle(self, schema):

        # Hide the administrative tabs for non-Managers
        # https://weblion.psu.edu/trac/weblion/wiki/FacultyStaffDirectoryExtender

        for hideme in ['User Settings', 'categorization', 'dates', 'ownership', 'settings']:
            for fieldName in schema.getSchemataFields(hideme):
                fieldName.widget.condition="python:member.has_role('Manager')"


        # Restrict the image field to Personnel Managers
        image_field = schema['image'].copy()
        image_field.widget.condition="python:member.has_role('Personnel Manager')"
        schema['image'] = image_field

        return schema


    def __init__(self, context):
        self.context = context

    def getFields(self):
        return self.fields
