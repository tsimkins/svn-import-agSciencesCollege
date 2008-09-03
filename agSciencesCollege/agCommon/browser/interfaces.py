from plone.theme.interfaces import IDefaultPloneLayer
from zope.viewlet.interfaces import IViewletManager
from plone.portlets.interfaces import IPortletManager

class IThemeSpecific(IDefaultPloneLayer):
    """Marker interface that defines a Zope 3 skin layer bound to a Skin
       Selection in portal_skins.
       If you need to register a viewlet only for the "agCommon"
       skin, this is the interface that must be used for the layer attribute
       in agCommon/browser/configure.zcml.
    """
    


class IAboveContentViews(IViewletManager):
    """A viewlet manager that sits above the content views
    """

class IBelowLeftColumn(IViewletManager):
    """A viewlet manager that sits above the content views
    """
    
class IAboveContentViewsFOOBAR(IPortletManager):
 """A description goes here    """