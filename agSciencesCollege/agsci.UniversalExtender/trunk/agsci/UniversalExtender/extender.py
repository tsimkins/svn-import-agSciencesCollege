from Products.Archetypes.public import StringField, StringWidget, BooleanField, BooleanWidget, TextField, RichWidget, LinesField, LinesWidget, InAndOutWidget, DateTimeField, CalendarWidget, ReferenceField, FileWidget, IntegerField, IntegerWidget
from Products.FacultyStaffDirectory.interfaces.person import IPerson
from Products.ATContentTypes.interfaces.event import IATEvent
from Products.ATContentTypes.interfaces.news import IATNewsItem
from Products.ATContentTypes.interfaces.document import IATDocument
from Products.ATContentTypes.interfaces.folder import IATFolder
from archetypes.schemaextender.field import ExtensionField
from archetypes.schemaextender.interfaces import ISchemaExtender, ISchemaModifier, IBrowserLayerAwareExtender
from interfaces import IUniversalExtenderLayer, IFSDPersonExtender, IDefaultExcludeFromNav, IFolderTopicExtender, ITopicExtender, IFolderExtender, IMarkdownDescriptionExtender, ITableOfContentsExtender, ITagExtender, IUniversalPublicationExtender
from zope.component import adapts, provideAdapter
from zope.interface import implements
from AccessControl import ClassSecurityInfo
from zope.interface import Interface
from Products.CMFCore.utils import getToolByName
from Products.agCommon.browser.interfaces import IContributors
from Products.CMFCore.interfaces import ISiteRoot
from agsci.subsite.content.interfaces import ITagRoot, IHomePage
from Products.Archetypes.utils import DisplayList
from collective.contentleadimage.extender import show_leadimage, leadimage_full_width
from archetypes.referencebrowserwidget import ReferenceBrowserWidget
from plone.app.blob.field import BlobField

class _ExtensionStringField(ExtensionField, StringField): pass
class _ExtensionBooleanField(ExtensionField, BooleanField): pass
class _TextExtensionField(ExtensionField, TextField): pass
class _ExtensionLinesField(ExtensionField, LinesField): pass
class _ExtensionDateTimeField(ExtensionField, DateTimeField): pass
class _ExtensionReferenceField(ExtensionField, ReferenceField): pass
class _ExtensionBlobField(ExtensionField, BlobField): pass
class _ExtensionIntegerField(ExtensionField, IntegerField): pass

class _TagsField(_ExtensionLinesField):
    def Vocabulary(self, context):
        tags = context.getAvailableTags()
        return DisplayList([(x,x) for x in tags])


# Add fax, twitter, facebook, linkedin to FSDPerson.
#
# Hide extraneous tabs from mere mortals. Hide image field from
# mere mortals so they can't upload a picture from 10 years ago
# when they were 20 pounds lighter and had hair. Professional
# portaits only!

class HomePageExtender(object):
    adapts(IHomePage)
    implements(ISchemaExtender, IBrowserLayerAwareExtender)
    layer = IUniversalExtenderLayer


    fields = [
        _ExtensionReferenceField(
            "slider_target",
            widget = ReferenceBrowserWidget(
                label=u"HomePage Slider",
                description=u"Choose an collection for the objects that will appear in the homepage slider.",
                show_path=True,
                condition="python:member.has_role('Manager', object)",
            ),
            schemata="settings",
            relationship = 'IsHomePageSliderFor',
            allowed_types = ('Topic',),
        ),
        _ExtensionBooleanField(
            "slider_random",
                required=False,
                searchable=False,
                default=True,
                widget=BooleanWidget(
                    label=u"Randomize HomePage Slider",
                    description=u"Display slider images in a random rather than sequential order.",
                    condition="python:member.has_role('Manager', object)",
                ),
            schemata="settings",
        ),
    ]

    def __init__(self, context):
        self.context = context

    def getFields(self):
        return self.fields


class FSDPersonExtender(object):
    adapts(IPerson)
    implements(ISchemaExtender, IBrowserLayerAwareExtender)
    layer = IUniversalExtenderLayer


    fields = [

        _ExtensionStringField(
            "faxNumber",
            required=False,
            schemata="Contact Information",
            widget=StringWidget(
                label=u"Office Fax",
                description=u"Example: 555-555-5555",
            ),
        ),
        _ExtensionStringField(
            "cellPhone",
            required=False,
            schemata="Contact Information",
            widget=StringWidget(
                label=u"Mobile",
                description=u"Example: 555-555-5555",
                visible={'edit':'invisible','view':'invisible'}
            ),
        ),
        _ExtensionStringField(
            "twitter_url",
            required=False,
            schemata="Social Media",
            widget=StringWidget(
                label=u"Twitter URL",
                description=u"Example: http://twitter.com/...",
            ),
            validators = ('isURL'),
        ),
        _ExtensionStringField(
            "facebook_url",
            required=False,
            schemata="Social Media",
            widget=StringWidget(
                label=u"Facebook URL",
                description=u"Example: http://www.facebook.com/...",
            ),
            validators = ('isURL'),
        ),
        _ExtensionStringField(
            "linkedin_url",
            required=False,
            schemata="Social Media",
            widget=StringWidget(
                label=u"Linked In",
                description=u"Example: http://www.linkedin.com/...",
            ),
            validators = ('isURL'),
        ),
        _ExtensionStringField(
            "primary_profile",
            required=False,
            schemata="settings",
            widget=StringWidget(
                label=u"Primary Profile URL",
                description=u"Providing a URL and setting the view to 'Person Alias' will redirect public users to this URL.",
                condition="python:member.has_role('Manager', object) or member.has_role('Personnel Manager', object)",
            ),
            validators = ('isURL'),
        ),
    ]

    def fiddle(self, schema):

        # Hide the administrative tabs for non-Managers
        # https://weblion.psu.edu/trac/weblion/wiki/FacultyStaffDirectoryExtender

        for hideme in ['User Settings', 'categorization', 'dates', 'ownership', 'settings']:
            for fieldName in schema.getSchemataFields(hideme):
                fieldName.widget.condition="python:member.has_role('Manager', object) or member.has_role('Personnel Manager', object)"

        # Check for "allow_person_image" in site_properties.  If it's not there and checked, remove the image.
        ptool = getToolByName(self.context, 'portal_properties')
        props = ptool.get("site_properties")

        if props and not props.getProperty('allow_person_image'):
            # Restrict the image field to Personnel Managers
            image_field = schema['image'].copy()
            image_field.widget.condition="python:member.has_role('Manager', object) or member.has_role('Personnel Manager', object)"
            schema['image'] = image_field

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
                fieldName.widget.condition="python:member.has_role('Manager', object) or member.has_role('Personnel Manager', object)"

        # Restrict the image field to Personnel Managers
        image_field = schema['image'].copy()
        image_field.widget.condition="python:member.has_role('Manager', object) or member.has_role('Personnel Manager', object)"
        schema['image'] = image_field

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
                label=u"Map To Location",
                description=u"e.g. Google Maps link",
            ),
        ),
        _ExtensionBooleanField(
            "free_registration",
                required=False,
                searchable=False,
                widget=BooleanWidget(
                    label=u"Enable online event registration (for no-fee events only).",
                    description=u"",
                    condition="python:member.has_role('Manager', object) or member.has_role('Event Organizer', object)",
                ),
        ),
        _ExtensionStringField(
            "free_registration_email",
                required=False,
                searchable=False,
                widget=StringWidget(
                    label=u"Email address for registration responses.",
                    description=u"Use this field if you would like to receive an email for each registration.",
                    condition="python:member.has_role('Manager', object) or member.has_role('Event Organizer', object)",
                ),
        ),
        _ExtensionDateTimeField(
            "free_registration_deadline",
                required=False,
                searchable=False,
                widget=CalendarWidget(
                    label=u"Registration deadline.",
                    description=u"Registrations will not be permitted after this date.",
                    condition="python:member.has_role('Manager', object) or member.has_role('Event Organizer', object)",
                ),
        ),
        _ExtensionIntegerField(
            "free_registration_attendee_limit",
                required=False,
                searchable=False,
                widget=IntegerWidget(
                    label=u"Maximum Attendees",
                    description=u"Additional registrations not be permitted after this number of registrations.",
                    condition="python:member.has_role('Manager', object) or member.has_role('Event Organizer', object)",
                ),
        ),
        _TextExtensionField(
            "free_registration_confirmation_message",
            required=False,
            widget=RichWidget(
                label=u"Email Confirmation Message",
                description=u"Additional text sent as part of confirmation email.",
            ),
            default_output_type="text/x-html-safe",
            validators=('isTidyHtmlWithCleanup',),
        ),
        _ExtensionBooleanField(
            "eventCanceled",
            required=False,
            default=False,
            widget=BooleanWidget(
                label=u"This event has been canceled",
                description=u"Check this box if an event has been canceled, and provide any addition information under 'Event Cancellation Information'",
            ),
        ),
        _TextExtensionField(
            "eventCanceledInfo",
            required=False,
            widget=RichWidget(
                label=u"Event Cancellation Information",
                description=u"",
            ),
            default_output_type="text/x-html-safe",
            validators=('isTidyHtmlWithCleanup',),
        ),

    ]

    def fiddle(self, schema):

        # Put map link after location
        try:
            schema.moveField('map_link', after='location')
        except KeyError:
            # This angers TalkEvents
            pass

        """
        # Maybe Plone 4 fixed the silly Event categorizations?
        # Move subject/tags to Categorization tab
        tmp_field = schema['eventType'].copy()
        tmp_field.schemata = 'categorization'
        schema['eventType'] = tmp_field

        # And put it before the related items
        schema.moveField('eventType', before='relatedItems')
        """
        # Hide the attendees field
        tmp_field = schema['attendees'].copy()
        tmp_field.widget.visible={'edit':'invisible','view':'invisible'}
        schema['attendees'] = tmp_field

        # Move text after the meta information
        schema.moveField('text', after='contactPhone')

        # Put eventCanceled after text
        try:
            schema.moveField('eventCanceled', after='text')
        except KeyError:
            # This angers TalkEvents
            pass

        # Put eventCanceledInfo after eventCanceled
        try:
            schema.moveField('eventCanceledInfo', after='eventCanceled')
        except KeyError:
            # This angers TalkEvents
            pass

        # Move dates above location
        schema.moveField('endDate', before='location')
        schema.moveField('startDate', before='endDate')

        return schema

    def __init__(self, context):
        self.context = context

    def getFields(self):
        return self.fields

# Add a field for an Article Link to the News Item type

class NewsItemExtender(object):
    adapts(IATNewsItem)
    implements(ISchemaExtender, ISchemaModifier, IBrowserLayerAwareExtender)
    layer = IUniversalExtenderLayer


    fields = [

        _ExtensionStringField(
            "article_link",
            required=False,
            widget=StringWidget(
                label=u"Article URL",
                description=u"Use this field if the article lives at another place on the internet. Do not copy/paste the full article text from another source.",
            ),
            validators = ('isURL'),
        ),

        show_leadimage,

        leadimage_full_width,

    ]

    def fiddle(self, schema):

        # Put map link after location
        try:
            schema.moveField('article_link', after="text")
        except KeyError:
            # This angers TalkEvents
            pass

        new_field = schema['text'].copy()
        new_field.widget.description = 'Use this rich text editor for news you create.'
        schema['text'] = new_field

        new_field = schema['image'].copy()
        new_field.widget.label = 'Lead image'
        new_field.widget.description = 'You can upload lead image. This image will be displayed above the content. Uploaded image will be automatically scaled to size specified in the leadimage control panel.'
        schema['image'] = new_field

        new_field = schema['imageCaption'].copy()
        new_field.widget.label = 'Lead image caption'
        new_field.widget.description = 'You may enter lead image caption text'
        schema['imageCaption'] = new_field

        # Move image_file after the article_link to match with other lead image
        schema.moveField('image', before='text')

        # Move image_caption as well
        schema.moveField('imageCaption', after='image')

        return schema

    def __init__(self, context):
        self.context = context

    def getFields(self):
        return self.fields

# Adds a "two column" field to folders. This will set a class, and jQuery will dynamically create two near-equal columns.

class FolderTopicExtender(object):
    adapts(IFolderTopicExtender)
    implements(ISchemaExtender, IBrowserLayerAwareExtender)
    layer = IUniversalExtenderLayer

    fields = [

        _ExtensionBooleanField(
            "show_description",
            required=False,
            default=True,
            schemata="settings",
            widget=BooleanWidget(
                label=u"Show description",
                description=u"This will show the description for each item in the folder listing.",
                condition="python:member.has_role('Manager', object)",
            ),
        ),

        _ExtensionBooleanField(
            "show_image",
            required=False,
            default=False,
            schemata="settings",
            widget=BooleanWidget(
                label=u"Show Lead Image in folder listing",
                description=u"This will show the lead image for each item in the folder listing.",
            ),
        ),

        _ExtensionBooleanField(
            "show_date",
            required=False,
            default=False,
            schemata="settings",
            widget=BooleanWidget(
                label=u"Show date",
                description=u"This will show the publication date for each item in the folder listing.",
                condition="python:member.has_role('Manager', object)",
            ),
        ),

        _ExtensionBooleanField(
            "show_description",
            required=False,
            default=True,
            schemata="settings",
            widget=BooleanWidget(
                label=u"Show description for contents",
                description=u"This will show the description for the items in the folder listing",
                condition="python:member.has_role('Manager', object)",
            ),
        ),

        _ExtensionBooleanField(
            "show_read_more",
            required=False,
            default=True,
            schemata="settings",
            widget=BooleanWidget(
                label=u"Show \"Read More...\"",
                description=u"This will show the \"Read More...\" for each item in the folder listing when using the Summary View.",
            ),
        ),

        _ExtensionBooleanField(
            "listing_after_text",
            required=False,
            default=False,
            schemata="settings",
            widget=BooleanWidget(
                label=u"Show text after folder contents",
                description=u"This will show the Body Text field after the folder contents instead of before.",
                condition="python:member.has_role('Manager', object)",
            ),
        ),

        _ExtensionBooleanField(
            "two_column",
            required=False,
            default=False,
            schemata="settings",
            widget=BooleanWidget(
                label=u"Two column display",
                description=u"This will automatically display the contents of the folder in two columns.  This is best for short titles/descriptions.",
                condition="python:member.has_role('Manager', object)",
            ),
        ),

    ]

    def __init__(self, context):
        self.context = context

    def getFields(self):
        return self.fields

"""
    Replaces the FolderText product.
"""

class FolderExtender(object):
    adapts(IFolderExtender)
    implements(ISchemaExtender, ISchemaModifier, IBrowserLayerAwareExtender)
    layer = IUniversalExtenderLayer

    fields = [
        _TextExtensionField('folder_text',
            required=False,
            widget=RichWidget(
                label="Body Text",
                label_msgid='folder_label_text',
                i18n_domain='Folder',
                description="",
            ),
            default_output_type="text/x-html-safe",
            searchable=True,
            validators=('isTidyHtmlWithCleanup',),
        ),

        _ExtensionBooleanField(
            "hide_exclude_from_nav",
            required=False,
            default=False,
            schemata="settings",
            widget=BooleanWidget(
                label=u"Hide items excluded from navigation in folder listing.",
                description=u"Hide items from folder listing if 'Exclude from navigation' is checked for those items.",
                condition="python:member.has_role('Manager', object)",
            ),
        ),

        _ExtensionBooleanField(
            "hide_subnavigation",
            required=False,
            default=False,
            schemata="settings",
            widget=BooleanWidget(
                label=u"Hide subnavigation when displaying the main folder listing.",
                description=u"",
                condition="python:member.has_role('Manager', object)",
            ),
        ),
    ]

    def __init__(self, context):
        self.context = context

    def getFields(self):
        return self.fields

    def fiddle(self, schema):

        # http://blog.keul.it/2011/09/plone-and-related-items-use-for.html
        # schema['relatedItems'].widget.visible['edit'] = 'invisible'

        tmp_field = schema['relatedItems'].copy()
        tmp_field.widget.visible={'edit':'visible','view':'visible'}
        tmp_field.widget.condition="python:member.has_role('Manager', object)"
        schema['relatedItems'] = tmp_field


class TopicExtender(object):
    adapts(ITopicExtender)
    implements(ISchemaExtender, ISchemaModifier, IBrowserLayerAwareExtender)
    layer = IUniversalExtenderLayer

    fields = [
        _ExtensionLinesField(
            "order_by_id",
                schemata="settings",
                required=False,
                widget = LinesWidget(
                    label=u"Order by id",
                    description=u"The content will show items with the listed ids first, and then sort by the default sort order.  One per line.",
            ),
        ),

        _ExtensionLinesField(
            "order_by_title",
                schemata="settings",
                required=False,
                widget = LinesWidget(
                    label=u"Order by Title",
                    description=u"The content will show items matching the specified regex patterns first, and then sort by the default sort order.  One per line.",
            ),
        ),
    ]


    def __init__(self, context):
        self.context = context

    def getFields(self):
        return self.fields

    def fiddle(self, schema):

        # Hide the 'Display as Table' and 'Table Columns' fields
        tmp_field = schema['customView'].copy()
        tmp_field.widget.visible={'edit':'invisible','view':'invisible'}
        schema['customView'] = tmp_field

        tmp_field = schema['customViewFields'].copy()
        tmp_field.widget.visible={'edit':'invisible','view':'invisible'}
        schema['customViewFields'] = tmp_field


# Adds a Markdown bool to render descriptions as Markdown

class MarkdownDescriptionExtender(object):
    adapts(IMarkdownDescriptionExtender)
    implements(ISchemaExtender, IBrowserLayerAwareExtender)
    layer = IUniversalExtenderLayer

    fields = [

        _ExtensionBooleanField(
            "render_description_as_markdown",
            required=False,
            default=False,
            schemata="settings",
            widget=BooleanWidget(
                label=u"Render description as Markdown",
                description=u"This will allow you to use Markdown formatting in the description field",
                condition="python:member.has_role('Manager', object)"
            ),
        ),
    ]


    def __init__(self, context):
        self.context = context

    def getFields(self):
        return self.fields

class TableOfContentsExtender(object):
    adapts(ITableOfContentsExtender)
    implements(ISchemaExtender, IBrowserLayerAwareExtender)
    layer = IUniversalExtenderLayer

    fields = [

        _ExtensionBooleanField(
            "tableContents",
            required=False,
            default=False,
            schemata="settings",
            widget=BooleanWidget(
                label=u"Table of contents",
                description=u"If selected, this will show a table of contents at the top of the page.",
            ),
        ),
    ]


    def __init__(self, context):
        self.context = context

    def getFields(self):
        return self.fields


# Change the "Contributors" field to "Contact Information"
# and add instructions

class ContributorsExtender(object):
    adapts(IContributors)
    implements(ISchemaModifier, IBrowserLayerAwareExtender)
    layer = IUniversalExtenderLayer

    def __init__(self, context):
        self.context = context

    def fiddle(self, schema):
        new_field = schema['contributors'].copy()
        new_field.widget.label = 'Contact Information'
        new_field.widget.description = 'Add the PSU id(s) of the article authors. For non-PSU individuals, add their information on a format of "Name|Job Title|E-mail"'
        schema['contributors'] = new_field

        return schema

# Add an "Allow comments on folder contents" checkbox to folders

class CommentsExtender(object):
    adapts(IATFolder)
    implements(ISchemaExtender, ISchemaModifier, IBrowserLayerAwareExtender)
    layer = IUniversalExtenderLayer

    fields = [

        _ExtensionBooleanField(
            "allow_discussion_contents",
            required=False,
            default=False,
            schemata="settings",
            widget=BooleanWidget(
                condition="python:member.has_role('Manager', object)",
                label=u"Allow comments on folder contents.",
                description=u"If selected, users can add comments to the items within this folder and its subfolders.",
            ),
        ),

    ]

    def fiddle(self, schema):
        schema.moveField('allow_discussion_contents', after='allowDiscussion')


    def __init__(self, context):
        self.context = context

    def getFields(self):
        return self.fields

# Adds the Public Tags field

class TagExtender(object):
    adapts(ITagExtender)
    implements(ISchemaExtender, ISchemaModifier, IBrowserLayerAwareExtender)
    layer = IUniversalExtenderLayer


    fields = [

        _TagsField(
            "public_tags",
            required=False,
            searchable=True,
            widget = InAndOutWidget(
                        label=u"Public Tags",
                        description=u"Tags for the article that are visible to the public.",
                        condition="python: object.getAvailableTags()",
            ),
        ),

    ]

    def __init__(self, context):
        self.context = context

    def getFields(self):
        return self.fields

# Tag Root (contains a list of tags)

class TagRootExtender(object):
    adapts(ITagRoot)
    implements(ISchemaExtender, ISchemaModifier, IBrowserLayerAwareExtender)
    layer = IUniversalExtenderLayer

    fields = [

        _ExtensionLinesField(
            "available_public_tags",
            required=False,
            widget = LinesWidget(
                label=u"Available public tags",
                description=u"Add the tags that will be available for contributors to this blog.",
            ),

        ),
    ]

    def fiddle(self, schema):

        schema.moveField('available_public_tags', after='folder_text')

        return schema

    def __init__(self, context):
        self.context = context

    def getFields(self):
        return self.fields


class UniversalPublicationExtender(object):
    adapts(IUniversalPublicationExtender)
    implements(ISchemaExtender, IBrowserLayerAwareExtender)

    layer = IUniversalExtenderLayer

    @property
    def fields(self):
        fields = self.custom_fields()
        fields.extend(self.base_fields())
        return fields

    def base_fields(self):
        return [

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

        ]

    def custom_fields(self):
        return []


    def __init__(self, context):
        self.context = context

    def getFields(self):
        return self.fields