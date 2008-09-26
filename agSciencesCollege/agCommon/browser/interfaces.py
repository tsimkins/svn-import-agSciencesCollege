from plone.theme.interfaces import IDefaultPloneLayer
from zope.viewlet.interfaces import IViewletManager
from plone.portlets.interfaces import IPortletManager
from plone.app.portlets.interfaces import IColumn

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
    
class IAdminlinks(IPortletManager):
	"""A description goes here    """
 
     
class IContact(IPortletManager):
	"""A description goes here    """
 
class IRightColumn(IPortletManager, IColumn):
	"""A viewlet manager that sits inside the main content area and floats to the right
	"""
	
class IHomepageImage(IPortletManager):
	"""A viewlet manager where you can create the homepage image
	"""
	
class ICenterColumn(IPortletManager, IColumn):
	"""A viewlet manager that sits inside the main content area.  Used for news on the front page
	"""