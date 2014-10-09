import zope.event
import zope.schema
from plone.portlets.interfaces import IPortletAssignment
from zope.component import adapts
from zope.interface import implements
from zope.formlib import form
from zope.lifecycleevent import ObjectCreatedEvent
from ZODB.POSException import ConflictError

from plone.portlet.collection.collection import Assignment as collection_assignment
from collective.portlet.feedmixer.portlet import Assignment as feedmixer_assignment
from collective.portlet.feedmixer.portlet.related import Assignment as feedmixer_related_assignment
from collective.portlet.feedmixer.portlet.similar import Assignment as feedmixer_similar_assignment
from plone.app.portlets.storage import PortletAssignmentMapping

from .interfaces import ICollectivePortletClassLayer, ICollectivePortletClass

def portletclass_fields(self):
    all_fields = zope.schema.getFieldsInOrder(ICollectivePortletClass)
    fields = []
    for (k,v) in all_fields:
        if filter_fields(self, k):
            fields.append((k,v))
    return fields

# A bunch of ugly logic to enable different fields on different portlet types
# and portlet managers
def filter_fields(self, k):

    # Only show mobile_navigation field in left column
    if k == 'mobile_navigation':

        # Get portlet manager
        try:
            manager = self.context.__parent__.__manager__
        except AttributeError:
            manager = ""

        if manager != 'plone.leftcolumn':
            return False


    # Only show More text related ones for collection and feedmixer
    if k in ('more_text', 'more_text_custom'):
        if isinstance(self.context, collection_assignment):
            return True
        elif isinstance(self.context, feedmixer_assignment) and not isinstance(self.context, feedmixer_related_assignment) and not isinstance(self.context, feedmixer_similar_assignment):
            return True
        else:
            return False

    # Only show parent_only on folderish objects
    if k in ('parent_only'):
        for o in self.aq_chain:
            if isinstance(o, PortletAssignmentMapping):
                if o.aq_parent.isPrincipiaFolderish:
                    return True

        return False

    # Irony: Disable collective_portletclass (the original purpose of this 
    # product) until we find a use case for it.
    
    if k in ('collective_portletclass', ):
        return False

    if k in ('portlet_width', 'portlet_item_count'):

        # Check to see if we're in the above or below portlet manager
        try:
            manager = self.context.__parent__.__dict__['__manager__']
            if 'ContentWellPortlets.BelowPortletManager' in manager or 'ContentWellPortlets.AbovePortletManager' in manager:
                return True
        except AttributeError, KeyError:
            pass
            
        # If layout is tile_homepage_view
        for o in self.aq_chain:
            if hasattr(o, 'getLayout'):
                return o.getLayout() == 'tile_homepage_view'

        return False


    return True
    
def collective_portletclass__init__(self, context, request):
    # Patch the __init__ methods of portlet add and edit forms to append the
    # portletclass field.
    self.context = context
    self.request = request
    if ICollectivePortletClassLayer.providedBy(self.request):
        for (k,v) in portletclass_fields(self):
            self.form_fields = self.form_fields + form.Fields(v)
    
    if hasattr(self, 'adjustedFields'):
        self.form_fields = self.adjustedFields()

def collective_portletclass_createAndAdd(self, data):
    # Patch the createAndAdd method of portlet add forms to remove the
    # portletclass field from the assignment creation data, setting it manually.
    
    ob = None
    
    if ICollectivePortletClassLayer.providedBy(self.request):
        for (k,v) in portletclass_fields(self):
            value = data[v.__name__]
            del data[v.__name__]
            ob = self.create(data)
            v.set(ob, value)

    if not ob:
        ob = self.create(data)

    zope.event.notify(ObjectCreatedEvent(ob))
    return self.add(ob)
#-------------------------------------------------------------------------------
# Duplicated from hexagonit.portletstyle
#-------------------------------------------------------------------------------
from plone.app.portlets.portlets import base
from plone.app.portlets.portlets import events
from plone.app.portlets.portlets import navigation
from plone.app.portlets.portlets import news
from plone.app.portlets.portlets import recent
from plone.app.portlets.portlets import rss
from plone.app.portlets.portlets import search


def base_assignment__init__(self, *args, **kwargs):
    self.portlet_style = kwargs.get('portlet_style', u' ')
    for (k,v) in kwargs.iteritems():
        if k == 'assignment_context_path':
            continue
        else:
            self.__setattr__(k, v)


# portlet.Events
def events_assignment__init__(self, *args, **kwargs):
    base.Assignment.__init__(self, *args, **kwargs)
    self.count = kwargs.get('count', 5)
    self.state = kwargs.get('state', ('published', ))


# portlet.Navigation
def navigation_assignment__init__(self, *args, **kwargs):
    base.Assignment.__init__(self, *args, **kwargs)
    self.name = kwargs.get('name', u"")
    self.root = kwargs.get('root', None)
    self.currentFolderOnly = kwargs.get('currentFolderOnly', False)
    self.includeTop = kwargs.get('includeTop', False)
    self.topLevel = kwargs.get('topLevel', 1)
    self.bottomLevel = kwargs.get('bottomLevel', 0)


# portlet.News
def news_assignment__init__(self, *args, **kwargs):
    base.Assignment.__init__(self, *args, **kwargs)
    self.count = kwargs.get('count', 5)
    self.state = kwargs.get('state', ('published', ))


# portlet.Recent
def recent_assignment__init__(self, *args, **kwargs):
    base.Assignment.__init__(self, *args, **kwargs)
    self.count = kwargs.get('count', 5)


# portlet.Rss
def rss_assignment__init__(self, *args, **kwargs):
    base.Assignment.__init__(self, *args, **kwargs)
    self.portlet_title = kwargs.get('portlet_title', u'')
    self.count = kwargs.get('count', 5)
    self.url = kwargs.get('url', u'')
    self.timeout = kwargs.get('timeout', 100)


# portlet.Search
def search_assignment__init__(self, *args, **kwargs):
    base.Assignment.__init__(self, *args, **kwargs)
    self.enableLivesearch = kwargs.get('enableLivesearch', u'')


# portlet.Static
def static_assignment__init__(self, *args, **kwargs):
    base.Assignment.__init__(self, *args, **kwargs)
    self.header = kwargs.get('header', u"")
    self.text = kwargs.get('text', u"")
    self.omit_border = kwargs.get('omit_border', False)
    self.footer = kwargs.get('footer', u"")
    self.more_url = kwargs.get('more_url', u"")


# portlet.Collection
def collection_assignment__init__(self, *args, **kwargs):
    base.Assignment.__init__(self, *args, **kwargs)
    self.header = kwargs.get('header', u"")
    self.target_collection = kwargs.get('target_collection', None)
    self.limit = kwargs.get('limit', None)
    self.random = kwargs.get('random', None)
    self.show_more = kwargs.get('show_more', True)
    self.show_dates = kwargs.get('show_dates', False)

#-------------------------------------------------------------------------------
# End duplicated from hexagonit.portletstyle
#-------------------------------------------------------------------------------
class CollectivePortletClass(object):
    """Adapter to provide default value"""
    adapts(IPortletAssignment)
    implements(ICollectivePortletClass)

    def __init__(self, context):
        self.context = context

    # collective_portletclass

    @property
    def collective_portletclass(self):
        return getattr(self.context, 'collective_portletclass', u'')

    @collective_portletclass.setter
    def collective_portletclass(self, value):
        if value:
            setattr(self.context, 'collective_portletclass', value)
        elif getattr(self.context, 'collective_portletclass', None) is not None:
            del self.context.collective_portletclass


    # mobile_navigation

    @property
    def mobile_navigation(self):
        return getattr(self.context, 'mobile_navigation', u'')

    @mobile_navigation.setter
    def mobile_navigation(self, value):
        if value:
            setattr(self.context, 'mobile_navigation', value)
        elif getattr(self.context, 'mobile_navigation', None) is not None:
            del self.context.mobile_navigation


    # parent_only
    
    @property
    def parent_only(self):
        return getattr(self.context, 'parent_only', u'')

    @parent_only.setter
    def parent_only(self, value):
        if value:
            setattr(self.context, 'parent_only', value)
        elif getattr(self.context, 'parent_only', None) is not None:
            del self.context.parent_only


    # more_text

    @property
    def more_text(self):
        return getattr(self.context, 'more_text', u'')

    @more_text.setter
    def more_text(self, value):
        if value:
            setattr(self.context, 'more_text', value)
        elif getattr(self.context, 'more_text', None) is not None:
            del self.context.more_text

    # more_text_custom

    @property
    def more_text_custom(self):
        return getattr(self.context, 'more_text_custom', u'')

    @more_text_custom.setter
    def more_text_custom(self, value):
        if value:
            setattr(self.context, 'more_text_custom', value)
        elif getattr(self.context, 'more_text_custom', None) is not None:
            del self.context.more_text_custom

    # portlet_width
    
    @property
    def portlet_width(self):
        return getattr(self.context, 'portlet_width', u'')

    @portlet_width.setter
    def portlet_width(self, value):
        if value:
            setattr(self.context, 'portlet_width', value)
        elif getattr(self.context, 'portlet_width', None) is not None:
            del self.context.portlet_width

    # portlet_item_count
    
    @property
    def portlet_item_count(self):
        return getattr(self.context, 'portlet_item_count', u'')

    @portlet_item_count.setter
    def portlet_item_count(self, value):
        if value:
            setattr(self.context, 'portlet_item_count', value)
        elif getattr(self.context, 'portlet_item_count', None) is not None:
            del self.context.portlet_item_count

# Patch for showing portlets only on parent object

def renderer_filter(self, portlets):
    filtered = []
    for p in portlets:
        try:
            if p['assignment'].available:
                if getattr(p['assignment'], 'parent_only', False):
                    if p['key'] != "/".join(self.context.getPhysicalPath()):
                        continue
                filtered.append(p)
        except ConflictError:
            raise
        except Exception, e:
            logger.exception(
                "Error while determining assignment availability of "
                "portlet (%r %r %r): %s" % ( 
                p['category'], p['key'], p['name'], str(e)))
    return filtered
