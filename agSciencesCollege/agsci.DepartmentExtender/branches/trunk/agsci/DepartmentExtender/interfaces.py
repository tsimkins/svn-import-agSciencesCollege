from zope.interface import Interface, Attribute
from plone.theme.interfaces import IDefaultPloneLayer

class IDepartmentExtenderLayer(IDefaultPloneLayer):
    """A Layer Specific to DepartmentExtender"""

class IResearchExtender(Interface):
    """ marker interface """
