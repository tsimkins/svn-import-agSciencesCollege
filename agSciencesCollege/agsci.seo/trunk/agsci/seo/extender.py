from Products.Archetypes.public import StringField, StringWidget, BooleanField, BooleanWidget, ReferenceField
from archetypes.referencebrowserwidget import ReferenceBrowserWidget
from Products.ATContentTypes.interface.interfaces import IATContentType
from archetypes.schemaextender.field import ExtensionField
from archetypes.schemaextender.interfaces import ISchemaExtender, IBrowserLayerAwareExtender
from interfaces import ISEOLayer, ICanonicalURLExtender
from zope.component import adapts
from zope.interface import implements

class _ExtensionStringField(ExtensionField, StringField): pass
class _ExtensionBooleanField(ExtensionField, BooleanField): pass
class _ExtensionReferenceField(ExtensionField, ReferenceField): pass

class RobotsExtender(object):
    adapts(IATContentType)
    implements(ISchemaExtender, IBrowserLayerAwareExtender)

    layer = ISEOLayer

    fields = [
        _ExtensionBooleanField(
            "exclude_from_robots",
            required=False,
            default=False,
            schemata="settings",
            widget=BooleanWidget(
                label=u"Exclude from search engines",
                description=u"Add to robots.txt file and add meta tag to header.",
                condition="python:member.has_role('Manager')",
            ),
        ),

    ]

    def __init__(self, context):
        self.context = context

    def getFields(self):
        return self.fields




class CanonicalURLExtender(object):
    adapts(ICanonicalURLExtender)
    implements(ISchemaExtender, IBrowserLayerAwareExtender)

    layer = ISEOLayer

    fields = [
        _ExtensionReferenceField(
            "canonical_url_ref",
            widget = ReferenceBrowserWidget(
                label=u"Canonical URL (Item)",
                description=u"Choose an item within this site",
                show_path=True,
                condition="python:member.has_role('Manager')",
            ),
            schemata="settings",
            relationship = 'IsCanonicalURLFor',
            allowed_types = ('Folder', 'Subsite', 'Section', 'Event', 'News Item', 'Document'),
        ),
        _ExtensionStringField(
            "canonical_url_text",
            widget = StringWidget(
                label=u"Canonical URL (External Resource)",
                description=u"Full URL",
                condition="python:member.has_role('Manager')",
            ),
            schemata="settings",
            validators = ('isURL'),
        ),
    ]

    def __init__(self, context):
        self.context = context

    def getFields(self):
        return self.fields

