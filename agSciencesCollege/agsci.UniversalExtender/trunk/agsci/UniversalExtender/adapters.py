from plone.app.portlets.portlets.navigation import NavtreeStrategy, INavigationPortlet 
from Products.CMFPlone.browser.navtree import SitemapNavtreeStrategy

from zope.interface import implements, Interface
from plone.app.layout.navigation.interfaces import INavtreeStrategy
from zope.component import adapts, getMultiAdapter, queryUtility

class CustomNavtreeStrategy(NavtreeStrategy):
    """The navtree strategy used for the default navigation portlet
    """
    implements(INavtreeStrategy)
    adapts(Interface, INavigationPortlet)

    def subtreeFilter(self, node):
        sitemapDecision = SitemapNavtreeStrategy.subtreeFilter(self, node)
        if sitemapDecision == False:
            return False
        if self.context.absolute_url() == node['getURL']:
            if getattr(self.context.aq_base, 'hide_subnavigation', False):
                return False
        depth = node.get('depth', 0)
        if depth > 0 and self.bottomLevel > 0 and depth >= self.bottomLevel:
            return False
        else:
            return True
