from zope.interface import Interface, Attribute
from plone.theme.interfaces import IDefaultPloneLayer

class IDepartmentExtenderLayer(IDefaultPloneLayer):
    """A Layer Specific to DepartmentExtender"""

class IResearchExtender(Interface):
    """ marker interface """

class IDepartmentExtenderUtilities(Interface):

    def isFaculty(self, o):
        pass

    def showResearchAreas(self, o):
        pass