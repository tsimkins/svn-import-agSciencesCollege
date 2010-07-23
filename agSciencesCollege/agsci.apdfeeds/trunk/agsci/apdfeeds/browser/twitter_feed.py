from zope.interface import implements

from Products.Five import BrowserView
from Products.CMFCore.utils import getToolByName

from agsci.apdfeeds import apdfeedsMessageFactory as _
from agsci.apdfeeds.browser.interfaces import IFeedDisplay
from agsci.apdfeeds.twitter import getItems
from Acquisition import aq_acquire, aq_inner

class FeedDisplay(BrowserView):
    """
    Feed Display browser view
    """
    implements(IFeedDisplay)

    def __init__(self, context, request):
        
        self.context = context
        self.request = request
        try:
            search_term = aq_acquire(self.context, 'twitter_search')
        except AttributeError:
            search_term = '#pennstate'
        
        self.title = "Twitter Results For %s" % search_term
        self.items = getItems(search_term)

    @property
    def portal_catalog(self):
        return getToolByName(self.context, 'portal_catalog')

    @property
    def portal(self):
        return getToolByName(self.context, 'portal_url').getPortalObject()

    def test(self):
        """
        test method
        """
        dummy = _(u'a dummy string')

        return {'dummy': dummy}
