from collective.portlet.feedmixer.interfaces import IFeedMixer
from collective.portlet.feedmixer.portlet import Renderer as _Renderer
from collective.portlet.feedmixer.portlet import Assignment as _Assignment
from collective.portlet.feedmixer.portlet import AddForm as _AddForm
from collective.portlet.feedmixer.portlet import EditForm as _EditForm
from plone.memoize.instance import memoize
from plone.app.portlets.portlets import base
from zope.interface import implements
from collective.portlet.feedmixer import FeedMixerMessageFactory as _
from zope import schema
from zope.formlib import form
import feedparser

def removeFields(form_fields):
    fields_to_remove = ['target_collection', 'show_footer', 'show_leadimage',
                        'alternate_footer_link', 'feeds', 'reverse_feed',]

    for i in fields_to_remove:
        if form_fields.get(i):
            form_fields = form_fields.omit(i)

    return form_fields

class IFeedMixerRelatedItems(IFeedMixer):
    pass

class Assignment(_Assignment):

    implements(IFeedMixerRelatedItems)


class AddForm(_AddForm):
    """Portlet add form.
    """
    form_fields = removeFields(form.Fields(IFeedMixerRelatedItems))


class EditForm(_EditForm):
    """Portlet edit form.
    """
    form_fields = removeFields(form.Fields(IFeedMixerRelatedItems))


class Renderer(_Renderer):

    @memoize
    def hasRelatedItems(self):
        return len(self.context.getRawRelatedItems()) > 0

    @property
    def allEntries(self):
        if self.hasRelatedItems():
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

        if self.hasRelatedItems():

            # This "old_header" logic works around the fact that
            # calling the RSS template sets the "Content-Type" header
            # to "text/xml", which causes validation errors because
            # the browser is trying to parse it as XML.

            original_header = self.request.response.getHeader('content-type')
            
            related_item_rss = self.context.restrictedTraverse('@@related_item_rss')
            
            feed = feedparser.parse(related_item_rss().encode("utf-8"))

            self.request.response.setHeader('Content-Type', original_header)
            return self.cleanFeed(feed)

        else:
            return None
        
    @property
    def show_footer(self):
        return False