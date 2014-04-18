from zope.interface import Interface, Attribute
from plone.theme.interfaces import IDefaultPloneLayer
from plone.app.portlets.portlets.navigation import INavigationPortlet

class IUniversalExtenderLayer(IDefaultPloneLayer):
    """A Layer Specific to UniversalExtender"""
    
class IFSDPersonExtender(Interface):
    """ marker interface """

class IDefaultExcludeFromNav(Interface):
    """ marker interface """
    
class IFolderTopicExtender(Interface):
    """ marker interface """
    
class ITopicExtender(Interface):
    """ marker interface """
    
class IFolderExtender(Interface, INavigationPortlet):
    """ marker interface """

class IMarkdownDescriptionExtender(Interface):
    """ marker interface """

class IFullWidthTableOfContentsExtender(Interface):
    """ marker interface """

class ITableOfContentsExtender(IFullWidthTableOfContentsExtender):
    """ marker interface """
    
class INoComments(Interface):
    """ marker interface """
    
class ITagExtender(Interface):
    """ marker interface """

class IEventModifiedEvent(Interface):
    context = Attribute("The content object that was saved.")

class ICustomNavigation(INavigationPortlet):
    """ marker interfaces """

class IUniversalPublicationExtender(Interface):
    """
        Marker interface to denote something as a "publication", which will add
        the necessary fields to it.
    """

class IFilePublicationExtender(Interface):
    """
        Marker interface to denote something as a "publication", which will add
        the necessary fields to it.
    """