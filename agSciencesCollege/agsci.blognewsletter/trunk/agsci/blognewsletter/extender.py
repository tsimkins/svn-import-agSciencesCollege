from Products.Archetypes.public import StringField, StringWidget, BooleanField, BooleanWidget, TextField, RichWidget, LinesField, LinesWidget, InAndOutWidget
from Products.ATContentTypes.interfaces.news import IATNewsItem
from archetypes.schemaextender.field import ExtensionField
from archetypes.schemaextender.interfaces import ISchemaExtender, IBrowserLayerAwareExtender
from interfaces import IBlogNewsletterLayer
from zope.component import adapts, provideAdapter
from zope.interface import implements
from AccessControl import ClassSecurityInfo
from zope.interface import Interface
from Products.CMFCore.utils import getToolByName
from Products.CMFCore.interfaces import ISiteRoot
from agsci.blognewsletter.content.interfaces import IBlog
from Products.Archetypes.utils import DisplayList

class _PublicTagsField(ExtensionField, LinesField):
    def Vocabulary(self, context):
        tags = context.getAvailableTags()
        return DisplayList([(x,x) for x in tags])

# Add a field for an Article Link to the News Item type

class NewsItemExtender(object):
    adapts(IATNewsItem)
    implements(ISchemaExtender, IBrowserLayerAwareExtender)
    layer = IBlogNewsletterLayer


    fields = [

        _PublicTagsField(
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

