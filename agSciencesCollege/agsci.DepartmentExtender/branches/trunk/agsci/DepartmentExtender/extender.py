from Products.Archetypes.public import LinesField, LinesWidget, InAndOutWidget
from Products.FacultyStaffDirectory.interfaces.person import IPerson
from archetypes.schemaextender.field import ExtensionField
from archetypes.schemaextender.interfaces import ISchemaExtender, ISchemaModifier, IBrowserLayerAwareExtender
from interfaces import IDepartmentExtenderLayer, IResearchExtender
from zope.component import adapts, provideAdapter
from zope.interface import implements
from zope.interface import Interface
from Products.CMFCore.utils import getToolByName
from Products.Archetypes.utils import DisplayList

class _ExtensionLinesField(ExtensionField, LinesField): pass

# Hardcode research areas
research_areas = [x.strip() for x in """
Advanced Agricultural and Food Systems
Biologically-Based Materials and Products
Environmental Resilience
Global Engagement
Integrated Health Solutions
""".strip().split("\n")]

# Custom field based on above areas
class _ResearchAreasField(_ExtensionLinesField):

    def Vocabulary(self, content_instance):

        return DisplayList([(x,x) for x in research_areas])
        

class ResearchExtender(object):
    adapts(IResearchExtender)
    implements(ISchemaExtender, IBrowserLayerAwareExtender)
    layer = IDepartmentExtenderLayer

    fields = [
        _ResearchAreasField(
            "department_research_areas",
                required=False,
                searchable=True,
                widget = InAndOutWidget(
                    label=u"Research Areas",
                    description=u"",
                    condition="python: object.restrictedTraverse('@@department_extender_utilities').showResearchAreas(object)",
                ),
        ),

    ]

    def __init__(self, context):
        self.context = context

    def getFields(self):
        return self.fields

class FSDPersonResearchExtender(ResearchExtender):
    adapts(IPerson)

    fields = [
        _ResearchAreasField(
            "department_research_areas",
                schemata="Professional Information",
                required=False,
                searchable=True,
                widget = InAndOutWidget(
                    label=u"Research Areas",
                    description=u"",
                    condition="python: object.restrictedTraverse('@@department_extender_utilities').isFaculty(object)",

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