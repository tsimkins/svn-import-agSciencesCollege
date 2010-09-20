from zope.interface import Interface
from plone.theme.interfaces import IDefaultPloneLayer

class IUniversalExtenderLayer(IDefaultPloneLayer):
    """A Layer Specific to UniversalExtender"""
    
class IFSDPersonExtender(Interface):
    """ marker interface """

class IDefaultExcludeFromNav(Interface):
    """ marker interface """