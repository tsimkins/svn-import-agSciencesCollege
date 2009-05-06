from zope.component import getSiteManager
from Products.FolderText.extender import FolderText

def install(portal):
    """Register the extender so it takes effect on this Plone site."""
    sm = getSiteManager(portal)
    # Local components are not per-container; they are per-sitemanager. It just so happens that every Plone site has a sitemanager. Hooray.
    sm.registerAdapter(FolderText, name='FolderText')
    
    return "Registered the extender at the root of the Plone site."

def uninstall(portal):
    """Unregister the schema extender so it no longer takes effect on this Plone site."""
    sm = getSiteManager(portal)
    sm.unregisterAdapter(FolderText, name='FolderText')
    
    return "Removed the extender from the root of the Plone site."
