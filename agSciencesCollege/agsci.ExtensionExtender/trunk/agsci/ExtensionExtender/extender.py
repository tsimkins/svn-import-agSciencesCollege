from Products.Archetypes.public import LinesField, InAndOutWidget, StringField, StringWidget
from Products.FacultyStaffDirectory.interfaces.person import IPerson
from archetypes.schemaextender.field import ExtensionField
from archetypes.schemaextender.interfaces import ISchemaExtender, ISchemaModifier, IBrowserLayerAwareExtender
from interfaces import IExtensionExtenderLayer, IExtensionExtender
from zope.component import adapts
from zope.interface import implements
from Products.Archetypes.utils import DisplayList
from Products.CMFCore.utils import getToolByName
from Acquisition import aq_acquire
from pdb import set_trace
from Products.CMFCore.interfaces import ISiteRoot

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

class _CountiesField(ExtensionField, LinesField):
    def Vocabulary(self, content_instance):

        ptool = getToolByName(content_instance, 'portal_properties')
        props = ptool.get("extension_properties")

        if props and props.extension_counties:
            return DisplayList([(x.strip(), x.strip()) for x in sorted(props.extension_counties)])
        else:
            return DisplayList([('N/A', 'N/A')])

    def getDefault(self, instance, **kwargs):

        for o in getAcquisitionChain(instance):
            try:
                v = self.get(o)
                
                if v:
                    return v
            except RuntimeError:
                continue

        return ()
          
class _ProgramsField(ExtensionField, LinesField):
    def Vocabulary(self, content_instance):

        ptool = getToolByName(content_instance, 'portal_properties')
        props = ptool.get("extension_properties")

        if props and props.extension_programs:
            return DisplayList([(x.strip(), x.strip()) for x in sorted(props.extension_programs)])
        else:
            return DisplayList([('N/A', 'N/A')])

    def getDefault(self, instance, **kwargs):

        for o in getAcquisitionChain(instance):
            try:
                v = self.get(o)
                
                if v:
                    return v
            except RuntimeError:
                continue

        return ()


class FSDExtensionExtender(object):
    adapts(IPerson)
    implements(ISchemaExtender, IBrowserLayerAwareExtender, ISchemaModifier)

    layer = IExtensionExtenderLayer
    
    fields = [
        _CountiesField(
            "extension_counties",
                schemata="categorization",
                required=False,
                widget = InAndOutWidget(
                label=u"Counties",
                description=u"Counties that this item is associated with",
            ),
        ),
        _ProgramsField(
            "extension_programs",
                schemata="categorization",
                required=False,
                widget = InAndOutWidget(
                label=u"Programs",
                description=u"Programs that this item is associated with",
            ),
        ),


    ]

    def __init__(self, context):
        self.context = context

    def getFields(self):
        return self.fields
        
    def fiddle(self, schema):

        # Restrict the image field to Personnel Managers
        
        for restricted_field in ['extension_counties', 'extension_programs']:
            tmp_field = schema[restricted_field].copy()
            tmp_field.widget.condition="python:member.has_role('Manager') or member.has_role('Personnel Manager')"
            schema[restricted_field] = tmp_field

        return schema
       
class ExtensionExtender(object):
    adapts(IExtensionExtender)
    implements(ISchemaExtender, IBrowserLayerAwareExtender)

    layer = IExtensionExtenderLayer
    
    fields = [
        _CountiesField(
            "extension_counties",
                schemata="categorization",
                required=False,
                widget = InAndOutWidget(
                label=u"Counties",
                description=u"Counties that this item is associated with",
            ),
        ),
        _ProgramsField(
            "extension_programs",
                schemata="categorization",
                required=False,
                widget = InAndOutWidget(
                label=u"Programs",
                description=u"Programs that this item is associated with",
            ),
        ),

    ]

    def __init__(self, context):
        self.context = context

    def getFields(self):
        return self.fields


