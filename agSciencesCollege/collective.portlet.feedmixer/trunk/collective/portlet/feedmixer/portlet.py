import itertools
import time
import feedparser

from zope.interface import implements
from zope.component import getMultiAdapter
from zope.component import getUtility

from plone.app.portlets.portlets import base
from plone.memoize.interfaces import ICacheChooser
from plone.memoize.instance import memoize

from zope.formlib import form
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from collective.portlet.feedmixer.interfaces import IFeedMixer

from plone.app.form.widgets.uberselectionwidget import UberSelectionWidget

import socket

import random

class Assignment(base.Assignment):
    """Portlet assignment.

    This is what is actually managed through the portlets UI and associated
    with columns.
    """
    implements(IFeedMixer)

    title = u"Feed Viewer"
    feeds = u""
    items_shown = 5
    show_header = False
    show_date = False
    show_event_info = False
    show_summary = False
    show_image = False
    show_footer = False
    alternate_footer_link = None
    reverse_feed = False
    cache_timeout = 900
    assignment_context_path = None
    target_collection = None
    image_position = 'right'
    image_size = 'small'
    random = False

    def __init__(self, title=title, feeds=feeds, items_shown=items_shown,
                 show_header=show_header, show_date=show_date,
                 show_event_info=show_event_info,
                 show_summary=show_summary,
                 show_image=show_image, show_footer=show_footer,
                 cache_timeout=cache_timeout,
                 alternate_footer_link=alternate_footer_link,
                 reverse_feed=reverse_feed,
                 assignment_context_path=assignment_context_path,
                 target_collection=target_collection, image_position=image_position,
                 image_size=image_size, random=random, *args, **kwargs):
        base.Assignment.__init__(self, *args, **kwargs)
        self.title=title
        self.feeds=feeds
        self.items_shown=items_shown
        self.show_header=show_header
        self.show_date=show_date
        self.show_event_info=show_event_info
        self.show_summary=show_summary
        self.show_image=show_image
        self.show_footer=show_footer
        self.alternate_footer_link=alternate_footer_link
        self.reverse_feed=reverse_feed
        self.cache_timeout=cache_timeout
        self.assignment_context_path = assignment_context_path
        self.target_collection = target_collection
        self.image_position = image_position
        self.image_size = image_size
        self.random = random

    def Title(self):
        """Returns the title. The function is used by Plone to render <title> correctly."""
        return self.title

class Renderer(base.Renderer):
    """Portlet renderer.
    """
    render = ViewPageTemplateFile("portlet.pt")

    @property
    def available(self):
        return bool(self.entries)

    @property
    def title(self):
        return self.data.title

    @property
    def show_header(self):
        return self.data.show_header

    @property
    def show_date(self):
        return self.data.show_date

    @property
    def show_event_info(self):
        return self.data.show_event_info

    @property
    def show_summary(self):
        return self.data.show_summary

    @property
    def show_image(self):
        return self.data.show_image

    @property
    def show_footer(self):
        return self.data.show_footer

    @property
    def target_collection(self):
        return self.data.target_collection

    @property
    def image_position(self):
        if self.data.image_position:
            return self.data.image_position
        else:
            return 'right'

    @property
    def random(self):
        if self.data.random:
            return self.data.random
        else:
            return False

    @property
    def image_size(self):
        if self.data.image_size:
            return self.data.image_size
        else:
            return 'small'

    @property
    def image_suffix(self):
        if self.image_size == 'large':
            return '_feedmixerlarge'
        else:
            return '_feedmixer'

    @property
    def is_printed_newsletter(self):
        return 'newsletter_print' in self.request.getURL()

    def contact_info(self, entry):
        info = []
        for k in ['agsci_eventcontactname', 'agsci_eventcontactemail', 'agsci_eventcontactphone']:
            if entry.get(k):
                info.append(entry.get(k))
        return ", ".join(info)

    @property
    def auto_more_url(self):
        context_path = self.data.assignment_context_path
        if context_path is not None:
            state=getMultiAdapter((self.context, self.request), name="plone_portal_state")
            portal=state.portal()
            context = portal.unrestrictedTraverse(context_path)
            return "%s/%s/full_feed" % \
                    (context.absolute_url(),
                     self.data.__name__)
        else:
            # Feedmixer portlets which were created before the context was
            # added need to be handled as well. They will still generate
            # wrong urls in subfolders.
            state=getMultiAdapter((self.context, self.request), name="plone_context_state")
            context = state.folder()
            return "%s/++contextportlets++%s/%s/full_feed" % \
                    (context.absolute_url(),
                     self.manager.__name__,
                     self.data.__name__)

    @property
    def more_url(self):

        alternate_footer_link = self.data.alternate_footer_link

        try:
            more_url = self.auto_more_url
        except:
            more_url = ""

        if alternate_footer_link:
            return str(alternate_footer_link).strip()
        elif self.data.target_collection and not self.feed_urls:
            # Collection URL (or if collection is default page, parent folder)
            collection = self.collection()
            if collection is None:
                return None
            else:
                parent = collection.getParentNode()
                if collection.id == parent.getDefaultPage():
                    return parent.absolute_url()
                else:
                    return collection.absolute_url()
        else:
            return more_url

    @property
    def feed_urls(self):
        if self.data.feeds:
            return (url.strip() for url in self.data.feeds.split())
        else:
            return ()

    def cleanFeed(self, feed):
        """Sanitize the feed.

        This function makes sure all feed and entry data we depend on us
        present and in proper form.
        """
        for entry in feed.entries:
            entry["feed"]=feed.feed
            if not "published_parsed" in entry:
                try:
                    entry["published_parsed"]=entry["updated_parsed"]
                    entry["published"]=entry["updated"]
                except KeyError:
                    entry["published_parsed"]=None
                    entry["published"]=None
                    entry["updated_parsed"]=None
                    entry["updated"]=None
        return feed

    def fetchFeed(self, url):

        # http://www.feedparser.org/docs/changes-41.html
        # I'm betting this is causing our hangs!

        # http://mxm-mad-science.blogspot.com/2009/01/small-trick-for-socket-timouts-in-plone.html
        # Resetting back to original timeout as soon as the call completes

        orig_timeout = socket.getdefaulttimeout()

        socket.setdefaulttimeout(10)

        feed=feedparser.parse(url)

        socket.setdefaulttimeout(orig_timeout)

        return self.cleanFeed(feed)

    def getFeed(self, url, collection=False):
        """Fetch a feed.

        This may return a cached result if the cache entry is considered to
        be fresh. Returned feeds have been cleaned using the cleanFeed method.
        """

        # Grab current time
        now=time.time()

        # Determine if we're anonymous
        portal_state = getMultiAdapter((self.context, self.request), name="plone_portal_state")
        isAnon = portal_state.anonymous()

        # If we're a collection, but not anonymous, run the query
        if collection and not isAnon:
            return self.collection_feed()

        # Start determining cached data
        chooser=getUtility(ICacheChooser)
        cache=chooser("collective.portlet.feedmixer.FeedCache")
        cached_data=cache.get(url, None)

        # If we don't have cached data, add a copy to cache and return the feed
        if not cached_data:

            if collection:
                feed = self.collection_feed()
            else:
                feed = self.fetchFeed(url)

            cache[url]=(now, feed)

            return feed

        else:

            (timestamp, cached_feed)=cached_data

            if cached_feed and (now <= (timestamp + self.data.cache_timeout)):
                return cached_feed

            if collection:
                feed = self.collection_feed()
            else:
                feed = self.fetchFeed(url)

            try:
                feed_status = feed.status
            except AttributeError:
                feed_status = 200

            if len(feed.get('entries', [])) == 0 or feed_status == 404:
                # If we don't have any entries (i.e. the feed is blank)
                # then just return the cached copy.
                return cached_feed
            else:
                cache[url]=(now, feed)
                return feed


    def mergeEntriesFromFeeds(self, feeds):
        if not feeds:
            return []
        if len(feeds)==1:
            return feeds[0].entries

        entries=list(itertools.chain(*(feed.entries for feed in feeds)))
        entries.sort(key=lambda x: x["published_parsed"], reverse=True)

        return entries

    # Removing because this breaks full.pt in Plone 4
    # Also, it seems to be caching logic ('mergeEntriesFromFeeds')
    # rather than data, so it's not really helping anything.
    # @request.cache(get_key=lambda func,self:self.data.feed_urls, get_request="self.request")

    @property
    def entries(self):
        return self.memoized_entries()
        
    @memoize
    def memoized_entries(self):
        entries = self.allEntries

        if len(entries) <= self.data.items_shown:
            return entries

        elif self.random:
            indexes = sorted(random.sample(range(0,len(entries)), self.data.items_shown))
            return [entries[x] for x in indexes]

        else:
            return entries[:self.data.items_shown]

    @property
    def allEntries(self):
        feeds=[self.getFeed(url) for url in self.feed_urls]

        if self.data.target_collection:
            feeds.append(self.getFeed(url=self.data.target_collection, collection=True))

        feeds=[feed for feed in feeds if feed is not None]

        entries=self.mergeEntriesFromFeeds(feeds)

        if self.data.reverse_feed:
            return [x for x in reversed(entries)]
        else:
            return entries

    @memoize
    def collection(self):

        collection_path = self.data.target_collection

        if not collection_path:
            return None

        if collection_path.startswith('/'):
            collection_path = collection_path[1:]

        if not collection_path:
            return None

        portal_state = getMultiAdapter((self.context, self.request), name=u'plone_portal_state')
        portal = portal_state.portal()
        if isinstance(collection_path, unicode):
            # restrictedTraverse accepts only strings
            collection_path = str(collection_path)

        return portal.restrictedTraverse(collection_path, default=None)

    @memoize
    def collection_feed(self):

        collection = self.collection()

        if collection:

            # This "old_header" logic works around the fact that
            # calling the RSS template sets the "Content-Type" header
            # to "text/xml", which causes validation errors because
            # the browser is trying to parse it as XML.

            original_header = self.request.response.getHeader('content-type')
            
            if self.random:
                # if we have a random option checked, we need to pull the full
                # RSS feed so we have the whole set to choose from.
                feed = feedparser.parse(collection.fullRSS().encode("utf-8"))
            else:
                feed = feedparser.parse(collection.RSS().encode("utf-8"))
            self.request.response.setHeader('Content-Type', original_header)
            return self.cleanFeed(feed)

        else:
            return None

class AddForm(base.AddForm):
    """Portlet add form.
    """
    form_fields = form.Fields(IFeedMixer)
    form_fields['target_collection'].custom_widget = UberSelectionWidget

    def create(self, data):
        path = self.context.__parent__.getPhysicalPath()
        return Assignment(assignment_context_path='/'.join(path), **data)


class EditForm(base.EditForm):
    """Portlet edit form.
    """
    form_fields = form.Fields(IFeedMixer)
    form_fields['target_collection'].custom_widget = UberSelectionWidget
