from collective.portlet.feedmixer.interfaces import IFeedMixerSimilarItems
from collective.portlet.feedmixer.portlet import AddForm as _AddForm
from collective.portlet.feedmixer.portlet import Assignment as _Assignment
from collective.portlet.feedmixer.portlet import EditForm as _EditForm
from collective.portlet.feedmixer.portlet import Renderer as _feedmixer_Renderer
from plone.memoize.instance import memoize
from zope import schema
from zope.formlib import form
from zope.interface import implements
import feedparser
from plone.app.portlets.portlets import base

from agsci.ExtensionExtender.portlet.similar import Renderer as _similar_Renderer

from collective.portlet.feedmixer import getFields as _getFields

def getFields():
    return _getFields(IFeedMixerSimilarItems, 
                        order=['title',  'show_header', 'cache_timeout', 'items_shown',],
                        remove=['target_collection', 
                                'show_footer', 
                                'show_leadimage',
                                'alternate_footer_link', 
                                'feeds', 
                                'reverse_feed', 
                                'header', 'limit', 'show_dates', 'show_location'])


class Assignment(_Assignment):
    implements(IFeedMixerSimilarItems)
    def __init__(self, *args, **kwargs):
        base.Assignment.__init__(self, *args, **kwargs)


class AddForm(_AddForm):
    """Portlet add form.
    """
    form_fields = getFields()

    def create(self, data):
        path = self.context.__parent__.getPhysicalPath()
        return Assignment(assignment_context_path='/'.join(path), **data)


class EditForm(_EditForm):
    """Portlet edit form.
    """
    form_fields = getFields()


class Renderer(_feedmixer_Renderer): #, _similar_Renderer):

    @property
    def allEntries(self):
    
        if self.context.isPrincipiaFolderish:
            return []

        feeds=[
            self.getFeed(url="/".join(self.context.getPhysicalPath()), collection=True)
        ]

        entries=self.mergeEntriesFromFeeds(feeds)

        return entries

    @memoize
    def collection(self):
        return self.context

    @memoize
    def collection_feed(self):

        # This "old_header" logic works around the fact that
        # calling the RSS template sets the "Content-Type" header
        # to "text/xml", which causes validation errors because
        # the browser is trying to parse it as XML.

        original_header = self.request.response.getHeader('content-type')

        similar_item_rss = self.context.restrictedTraverse('@@similar_item_rss')

        feed = feedparser.parse(similar_item_rss(
                    limit=self.data.items_shown, 
                    query_portal_type=self.data.query_portal_type, 
                    query_counties=self.data.query_counties, 
                    query_programs=self.data.query_programs,
                    query_topics=self.data.query_topics,
                    query_courses=self.data.query_courses,
                    query_title=self.data.query_title,
                    days=self.data.days,
                    random=self.data.random,
        ).encode("utf-8"))

        self.request.response.setHeader('Content-Type', original_header)

        return self.cleanFeed(feed)

    @property
    def show_footer(self):
        return False