from Products.Archetypes.public import LinesField, InAndOutWidget, StringField, StringWidget, LinesWidget, BooleanField, BooleanWidget, FileWidget, SelectionWidget
from Products.FacultyStaffDirectory.interfaces.person import IPerson
from archetypes.schemaextender.field import ExtensionField
from archetypes.schemaextender.interfaces import ISchemaExtender, ISchemaModifier, IBrowserLayerAwareExtender
from interfaces import IExtensionExtenderLayer, IExtensionExtender, IExtensionPublicationExtender
from zope.component import adapts
from zope.interface import implements
from Products.Archetypes.utils import DisplayList
from Products.CMFCore.utils import getToolByName
from Acquisition import aq_acquire, aq_chain
from Products.CMFCore.interfaces import ISiteRoot
from plone.app.blob.field import BlobField
from Products.ATContentTypes.interfaces.event import IATEvent

class _ExtensionStringField(ExtensionField, StringField): pass
class _ExtensionBooleanField(ExtensionField, BooleanField): pass
class _ExtensionBlobField(ExtensionField, BlobField): pass

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

class _CoursesField(_ExtensionLinesField):
    def Vocabulary(self, content_instance):

        extension_courses_tool = getToolByName(content_instance, 'extension_course_tool')

        if extension_courses_tool:
            courses = [('', 'Select a course...'),]
            courses.extend([(x.strip(), x.strip()) for x in extension_courses_tool.getCourses()])
            return DisplayList(courses)
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

        _TopicsField(
            "extension_topics",
                schemata="Professional Information",
                required=False,
                searchable=True,
                widget = InAndOutWidget(
                label=u"Programs",
                description=u"Extension programs that this item is associated with",
            ),
        ),

        _SubtopicsField(
            "extension_subtopics",
                schemata="Professional Information",
                required=False,
                searchable=True,
                widget = InAndOutWidget(
                label=u"Topics",
                description=u"Topics within the program(s) that this item is associated with",
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

        _ProgramsField(
            "extension_programs",
                schemata="Professional Information",
                required=False,
                searchable=True,
                widget = InAndOutWidget(
                label=u"Legacy Programs",
                description=u"This is only for compatibility purposes and will be removed shortly.",
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
        _TopicsField(
            "extension_topics",
                schemata="categorization",
                required=False,
                searchable=True,
                widget = InAndOutWidget(
                label=u"Programs",
                description=u"Extension programs that this item is associated with",
            ),
        ),
        _SubtopicsField(
            "extension_subtopics",
                schemata="categorization",
                required=False,
                searchable=True,
                widget = InAndOutWidget(
                label=u"Topics",
                description=u"Topics within the program(s) that this item is associated with",
            ),
        ),
        _ProgramsField(
            "extension_programs",
                schemata="categorization",
                required=False,
                searchable=True,
                widget = InAndOutWidget(
                label=u"Legacy Programs",
                description=u"This is only for compatibility purposes and will be removed shortly.",
            ),
        ),
    ]

    def __init__(self, context):
        self.context = context

    def getFields(self):
        return self.fields




#--
class ExtensionPublicationExtender(object):
    adapts(IExtensionPublicationExtender)
    implements(ISchemaExtender, IBrowserLayerAwareExtender)

    layer = IExtensionExtenderLayer
    
    fields = [
        _ExtensionStringField(
            "extension_publication_code",
                schemata="Publication",
                required=False,
                searchable=True,
                widget=StringWidget(
                    label=u"Publication Code",
                    description=u"",
                ),
        ),

        _ExtensionStringField(
            "extension_publication_series",
                schemata="Publication",
                required=False,
                searchable=True,
                widget=StringWidget(
                    label=u"Publication Series",
                    description=u"Optional",
                ),
        ),

        _ExtensionStringField(
            "extension_publication_url",
                schemata="Publication",
                required=False,
                searchable=False,
                widget=StringWidget(
                    label=u"External Publication URL",
                    description=u"",
                ),
                validators = ('isURL'),
        ),

        _ExtensionBlobField(
            "extension_publication_file",
            schemata="Publication",
            required=False,
            widget=FileWidget(
                label=u"Publication file",
                description=u"",
            ),
        ),

        _ExtensionBooleanField(
            "extension_publication_download",
            schemata="Publication",
            required=False,
            default=False,
            widget=BooleanWidget(
                label=u"Automatically generate PDF",
                description=u"Verify the formatting of this PDF after checking this box. You may have to tweak the content to obtain a nicely formatted PDF.",
            ),
        ),

        _ExtensionBooleanField(
            "extension_publication_description_body",
            schemata="Publication",
            required=False,
            default=False,
            widget=BooleanWidget(
                label=u"Show description in body rather than header.",
                description=u"",
            ),
        ),

        _ExtensionBooleanField(
            "extension_publication_long_statement",
            schemata="Publication",
            required=False,
            default=False,
            widget=BooleanWidget(
                label=u"Show long statement on generated PDF.",
                description=u"",
            ),
        ),
        


    ]

    def __init__(self, context):
        self.context = context

    def getFields(self):
        return self.fields


class ExtensionEventExtender(object):
    adapts(IATEvent)
    implements(ISchemaExtender, ISchemaModifier, IBrowserLayerAwareExtender)

    layer = IExtensionExtenderLayer
    
    fields = [
        _CoursesField(
            "extension_courses",
                required=False,
                searchable=True,
                widget = SelectionWidget(
                label=u"Course",
                description=u"Course that this event is associated with",
                format='select'
            ),
        ),
    ]
    
    def fiddle(self, schema):
        # Make "Location" mandatory
        tmp_field = schema['location'].copy()
        tmp_field.required=True
        schema['location'] = tmp_field

        # Put courses before location
        schema.moveField('extension_courses', after='location')

        return schema

    def __init__(self, context):
        self.context = context

    def getFields(self):
        return self.fields