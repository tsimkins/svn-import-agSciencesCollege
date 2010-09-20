from Products.Archetypes.public import ImageField, ImageWidget, StringField, StringWidget
from Products.FacultyStaffDirectory.interfaces.person import IPerson
from Products.ATContentTypes.interface.event import IATEvent
from archetypes.schemaextender.field import ExtensionField
from archetypes.schemaextender.interfaces import ISchemaExtender, ISchemaModifier, IBrowserLayerAwareExtender
from interfaces import IUniversalExtenderLayer, IFSDPersonExtender, IDefaultExcludeFromNav
from zope.component import adapts
from zope.interface import implements
import pdb
from AccessControl import ClassSecurityInfo


class _ExtensionStringField(ExtensionField, StringField): pass

# Add fax, twitter, facebook, linkedin to FSDPerson.
#
# Hide extraneous tabs from mere mortals. Hide image field from
# mere mortals so they can't upload a picture from 10 years ago
# when they were 20 pounds lighter and had hair. Professional
# portaits only!


class FSDPersonExtender(object):
    adapts(IPerson)
    implements(ISchemaExtender, IBrowserLayerAwareExtender)
    layer = IUniversalExtenderLayer


    fields = [

        _ExtensionStringField(
            "fax",
            required=False,
            schemata="Contact Information",
            widget=StringWidget(
                label=u"Office Fax",
                description=u"Example: 555-555-5555",
            ),
        ),
        _ExtensionStringField(
            "twitter",
            required=False,
            schemata="Social Media",
            widget=StringWidget(
                label=u"Twitter URL",
                description=u"Example: http://twitter.com/...",
            ),
        ),
        _ExtensionStringField(
            "facebook",
            required=False,
            schemata="Social Media",
            widget=StringWidget(
                label=u"Facebook URL",
                description=u"Example: http://www.facebook.com/...",
            ),
        ),
        _ExtensionStringField(
            "linkedin",
            required=False,
            schemata="Social Media",
            widget=StringWidget(
                label=u"Linked In",
                description=u"Example: http://www.linkedin.com/...",
            ),
        ),
    ]

    def fiddle(self, schema):

        # Hide the administrative tabs for non-Managers
        # https://weblion.psu.edu/trac/weblion/wiki/FacultyStaffDirectoryExtender
        
        for hideme in ['User Settings', 'categorization', 'dates', 'ownership', 'settings']:
            for fieldName in schema.getSchemataFields(hideme):
                fieldName.widget.condition="python:member.has_role('Manager') or member.has_role('Personnel Manager')"

        # Restrict the image field to Personnel Managers
        image_field = schema['image'].copy()
        image_field.widget.condition="python:member.has_role('Manager') or member.has_role('Personnel Manager')"
        schema['image'] = image_field

        #pdb.set_trace()

        return schema

    def __init__(self, context):
        self.context = context

    def getFields(self):
        return self.fields

"""
# Hide extraneous tabs from mere mortals. Hide image field from
# mere mortals so they can't upload a picture from 10 years ago
# when they were 20 pounds lighter and had hair. Professional
# portaits only!

class FSDPersonModifier(object):
    adapts(IPerson)
    implements(ISchemaModifier, IBrowserLayerAwareExtender)
    layer = IUniversalExtenderLayer

    security = ClassSecurityInfo()

    def __init__(self, context):
        self.context = context

    from Products.FacultyStaffDirectory.Person import schema


    def fiddle(self, schema):

        # Hide the administrative tabs for non-Managers
        # https://weblion.psu.edu/trac/weblion/wiki/FacultyStaffDirectoryExtender
        
        for hideme in ['User Settings', 'categorization', 'dates', 'ownership', 'settings']:
            for fieldName in schema.getSchemataFields(hideme):
                fieldName.widget.condition="python:member.has_role('Manager') or member.has_role('Personnel Manager')"

        # Restrict the image field to Personnel Managers
        image_field = schema['image'].copy()
        image_field.widget.condition="python:member.has_role('Manager') or member.has_role('Personnel Manager')"
        schema['image'] = image_field

        #pdb.set_trace()

        return schema
"""

# Check the "Exclude from navigation" by default for Links
# and Files.  99% of the time these should be hidden, but
# occasionally they need a link or file to show up in the 
# navigation.  Can't do PhotoFolders, since they are a
# clone of ATFolder, and it would be really ugly to extend
# the base class, and put in a check to see if it's a 
# specific type.

class DefaultExcludeFromNav(object):
    adapts(IDefaultExcludeFromNav)
    implements(ISchemaModifier, IBrowserLayerAwareExtender)
    layer = IUniversalExtenderLayer

    def __init__(self, context):
        self.context = context

    def fiddle(self, schema):
        # Set the default for "Exclude from nav" to true
        exclude_field = schema['excludeFromNav'].copy()
        exclude_field.default = True
        schema['excludeFromNav'] = exclude_field

        return schema
        

# Add a field for a Google Map link to the Event type

class EventExtender(object):
    adapts(IATEvent)
    implements(ISchemaExtender, ISchemaModifier, IBrowserLayerAwareExtender)
    layer = IUniversalExtenderLayer


    fields = [

        _ExtensionStringField(
            "map_link",
            required=False,
            widget=StringWidget(
                label=u"Map To Event",
                description=u"e.g. Google Maps link",
            ),
        ),

    ]

    def fiddle(self, schema):

        # Put map link after location
        schema.moveField('map_link', after='location')
        #pdb.set_trace()

        # Move subject/tags to Categorization tab
        tmp_field = schema['eventType'].copy()
        tmp_field.schemata = 'categorization'
        schema['eventType'] = tmp_field

        # And put it before the related items
        schema.moveField('eventType', before='relatedItems')
               
        # Hide the attendees field
        tmp_field = schema['attendees'].copy()
        tmp_field.widget.visible={'edit':'invisible','view':'invisible'}
        schema['attendees'] = tmp_field

        # Move text after the meta information
        schema.moveField('text', after='contactPhone')

        # Move dates above location
        schema.moveField('endDate', before='location')
        schema.moveField('startDate', before='endDate')
        
        return schema

    def __init__(self, context):
        self.context = context

    def getFields(self):
        return self.fields
