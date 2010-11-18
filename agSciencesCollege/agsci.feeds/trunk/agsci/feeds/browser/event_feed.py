from zope.interface import implements

from Products.Five import BrowserView
from Products.CMFCore.utils import getToolByName

from agsci.feeds import feedsMessageFactory as _
from agsci.feeds.browser.interfaces import IFeedDisplay
from agsci.feeds import texttime
from DateTime import DateTime
from datetime import timedelta

class FeedDisplay(BrowserView):
    """
    Feed Display browser view
    """
    implements(IFeedDisplay)

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.title = "Upcoming Events"


        # Five minutes ago        
        from_date = DateTime() - (5.0/(24*60))
        
        self.items = []
        
        search_results = self.portal_catalog.searchResults({'portal_type' : 'Event', 
                                                            'start' : {'query' : (from_date), 'range' : 'min'},
                                                            'sort_on' : 'start' })
                                                            
        for brain in search_results:
        
            current_time = DateTime()
            item_time = brain.start
            if current_time > item_time:    
                time_text = "%s ago" % texttime.stringify(timedelta(current_time - item_time))
            else:
                time_text = "in %s" % texttime.stringify(timedelta(item_time - current_time))
        
            self.items.append({
                'title' : brain.Title,
                'author' : None,
                'item_time' : time_text,
                'author_image' : None,
                'location' : brain.location,
                'item_start' : brain.start, 
            })
            

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
