from Products.Archetypes.public import LinesField, InAndOutWidget, StringField, StringWidget, LinesWidget
from Products.FacultyStaffDirectory.interfaces.person import IPerson
from archetypes.schemaextender.field import ExtensionField
from archetypes.schemaextender.interfaces import ISchemaExtender, ISchemaModifier, IBrowserLayerAwareExtender
from interfaces import IExtensionExtenderLayer, IExtensionExtender
from zope.component import adapts
from zope.interface import implements
from Products.Archetypes.utils import DisplayList
from Products.CMFCore.utils import getToolByName
from Acquisition import aq_acquire
from Products.CMFCore.interfaces import ISiteRoot


class _ExtensionLinesField(ExtensionField, LinesField):

    def getDefault(self, instance, **kwargs):
        for o in getAcquisitionChain(instance):
            try:
                v = self.get(o)
                
                if v:
                    return v
            except:
                continue

        return ()


# From http://plone.org/documentation/manual/plone-community-developer-documentation/serving/traversing

def getAcquisitionChain(object):
    """
    @return: List of objects from context, its parents to the portal root

    Example::

        chain = getAcquisitionChain(self.context)
        print "I will look up objects:" + str(list(chain))

    @param object: Any content object
    @return: Iterable of all parents from the direct parent to the site root
    """

    # It is important to use inner to bootstrap the traverse,
    # or otherwise we might get surprising parents
    # E.g. the context of the view has the view as the parent
    # unless inner is used
    inner = object.aq_inner

    iter = inner

    while iter is not None:
        yield iter

        if ISiteRoot.providedBy(iter):
           break

        if not hasattr(iter, "aq_parent"):
            raise RuntimeError("Parent traversing interrupted by object: " + str(parent))

        iter = iter.aq_parent

class _TopicsField(_ExtensionLinesField):
    def Vocabulary(self, content_instance):

        ptool = getToolByName(content_instance, 'portal_properties')
        props = ptool.get("extension_properties")

        if props and props.extension_topics:
            return DisplayList([(x.strip(), x.strip()) for x in sorted(props.extension_topics)])
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

    ]

    def __init__(self, context):
        self.context = context

    def getFields(self):
        return self.fields


