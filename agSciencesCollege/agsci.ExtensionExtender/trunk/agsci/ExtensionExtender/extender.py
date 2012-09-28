from Products.Archetypes.public import LinesField, InAndOutWidget, StringField, StringWidget, LinesWidget
from Products.FacultyStaffDirectory.interfaces.person import IPerson
from archetypes.schemaextender.field import ExtensionField
from archetypes.schemaextender.interfaces import ISchemaExtender, ISchemaModifier, IBrowserLayerAwareExtender
from interfaces import IExtensionExtenderLayer, IExtensionExtender
from zope.component import adapts
from zope.interface import implements
from Products.Archetypes.utils import DisplayList
from Products.CMFCore.utils import getToolByName
from Acquisition import aq_acquire, aq_chain
from Products.CMFCore.interfaces import ISiteRoot


class _ExtensionLinesField(ExtensionField, LinesField):

    def getDefault(self, instance, **kwargs):
        # Shortcut this field when creating non News Item/Events.  Specifically,
        # This prevents the lookup when creating folders.

        if instance.portal_type not in ['News Item', 'Event']:
            return ()

        for i in aq_chain(instance):
            if ISiteRoot.providedBy(i):
                break
            else:
                try:
                    v = self.get(i)
                    
                    if v:
                        return v
                except:
                    break

        return ()

    def get(self, instance, **kwargs):     
        __traceback_info__ = (self.getName(), instance, kwargs)
        try:
            kwargs['field'] = self
            return self.getStorage(instance).get(self.getName(), instance, **kwargs)
        except AttributeError:  
            return ()




class _TopicsField(_ExtensionLinesField):
    def Vocabulary(self, content_instance):

        ptool = getToolByName(content_instance, 'portal_properties')
        props = ptool.get("extension_properties")

        if props and props.extension_topics:
            return DisplayList([(x.strip(), x.strip()) for x in sorted(props.extension_topics)])
        else:
            return DisplayList([('N/A', 'N/A')])

class _SubtopicsField(_ExtensionLinesField):
    def Vocabulary(self, content_instance):

        ptool = getToolByName(content_instance, 'portal_properties')
        props = ptool.get("extension_properties")

        if props and props.extension_subtopics:
            return DisplayList([(x.strip(), x.strip()) for x in sorted(props.extension_subtopics)])
        else:
            return DisplayList([('N/A', 'N/A')])

class _CountiesField(_ExtensionLinesField):
    def Vocabulary(self, content_instance):

        ptool = getToolByName(content_instance, 'portal_properties')
        props = ptool.get("extension_properties")

        if props and props.extension_counties:
            return DisplayList([(x.strip(), x.strip()) for x in sorted(props.extension_counties)])
        else:
            return DisplayList([('N/A', 'N/A')])

class _ProgramsField(_ExtensionLinesField):
    def Vocabulary(self, content_instance):

        ptool = getToolByName(content_instance, 'portal_properties')
        props = ptool.get("extension_properties")

        if props and props.extension_programs:
            return DisplayList([(x.strip(), x.strip()) for x in sorted(props.extension_programs)])
        else:
            return DisplayList([('N/A', 'N/A')])

class FSDExtensionExtender(object):
    adapts(IPerson)
    implements(ISchemaExtender, IBrowserLayerAwareExtender, ISchemaModifier)

    layer = IExtensionExtenderLayer
    
    fields = [
        _CountiesField(
            "extension_counties",
                schemata="Professional Information",
                required=False,
                searchable=True,
                widget = InAndOutWidget(
                label=u"Counties",
                description=u"Counties that this person is associated with",
            ),
        ),

        _ProgramsField(
            "extension_programs",
                schemata="Professional Information",
                required=False,
                searchable=True,
                widget = InAndOutWidget(
                label=u"Programs",
                description=u"Programs that this person is associated with",
            ),
        ),

        _TopicsField(
            "extension_topics",
                schemata="Professional Information",
                required=False,
                searchable=True,
                widget = InAndOutWidget(
                label=u"Topics",
                description=u"Topics that this person is associated with",
            ),
        ),

        _SubtopicsField(
            "extension_subtopics",
                schemata="Professional Information",
                required=False,
                searchable=True,
                widget = InAndOutWidget(
                label=u"Subtopics",
                description=u"Subtopics that this person is associated with",
            ),
        ),
        _ExtensionLinesField(
            "extension_areas",
                schemata="Professional Information",
                required=False,
                searchable=True,
                widget = LinesWidget(
                    label=u"Areas of Expertise",
                    description=u"One per line",
            ),
        ),


    ]

    def __init__(self, context):
        self.context = context

    def getFields(self):
        return self.fields
        
class ExtensionExtender(object):
    adapts(IExtensionExtender)
    implements(ISchemaExtender, IBrowserLayerAwareExtender)

    layer = IExtensionExtenderLayer
    
    fields = [
        _CountiesField(
            "extension_counties",
                schemata="categorization",
                required=False,
                searchable=True,
                widget = InAndOutWidget(
                label=u"Counties",
                description=u"Counties that this item is associated with",
            ),
        ),
        _ProgramsField(
            "extension_programs",
                schemata="categorization",
                required=False,
                searchable=True,
                widget = InAndOutWidget(
                label=u"Programs",
                description=u"Programs that this item is associated with",
            ),
        ),
        _TopicsField(
            "extension_topics",
                schemata="categorization",
                required=False,
                searchable=True,
                widget = InAndOutWidget(
                label=u"Topics",
                description=u"Topics that this item is associated with",
            ),
        ),
        _SubtopicsField(
            "extension_subtopics",
                schemata="categorization",
                required=False,
                searchable=True,
                widget = InAndOutWidget(
                label=u"Subtopics",
                description=u"Subtopics that this item is associated with",
            ),
        ),
    ]

    def __init__(self, context):
        self.context = context

    def getFields(self):
        return self.fields


