from zope.interface import Interface
from plone.theme.interfaces import IDefaultPloneLayer

class IExtensionExtenderLayer(IDefaultPloneLayer):
    """A Layer Specific to StartingPoint"""

class IExtensionExtender(Interface):
    """ marker interface """
    
class IExtensionPublicationExtender(Interface):
    """
        Marker interface to denote something as a "publication", which will add
        the necessary fields to it.
    """

class IExtensionCountiesExtender(Interface):
    """
        Marker interface which allows us to a
    """