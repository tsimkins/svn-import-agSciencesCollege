import zope.event
import zope.schema
from plone.portlets.interfaces import IPortletAssignment
from zope.component import adapts
from zope.interface import implements
from zope.formlib import form
from zope.lifecycleevent import ObjectCreatedEvent

from .interfaces import ICollectivePortletClassLayer, ICollectivePortletClass

portletclass_fields = zope.schema.getFieldsInOrder(ICollectivePortletClass)

def collective_portletclass__init__(self, context, request):
    # Patch the __init__ methods of portlet add and edit forms to append the
    # portletclass field.
    self.context = context
    self.request = request
    if ICollectivePortletClassLayer.providedBy(self.request):
        for (k,v) in portletclass_fields:
            self.form_fields = self.form_fields + form.Fields(v)

def collective_portletclass_createAndAdd(self, data):
    # Patch the createAndAdd method of portlet add forms to remove the
    # portletclass field from the assignment creation data, setting it manually.
    if ICollectivePortletClassLayer.providedBy(self.request):
        for (k,v) in portletclass_fields:
            value = data[v.__name__]
            del data[v.__name__]
            ob = self.create(data)
            v.set(ob, value)
    else:
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

    @property
    def collective_portletclass(self):
        return getattr(self.context, 'collective_portletclass', u'')

    @collective_portletclass.setter
    def collective_portletclass(self, value):
        if value:
            setattr(self.context, 'collective_portletclass', value)
        elif getattr(self.context, 'collective_portletclass', None) is not None:
            del self.context.collective_portletclass

    @property
    def mobile_navigation(self):
        return getattr(self.context, 'mobile_navigation', u'')

    @mobile_navigation.setter
    def mobile_navigation(self, value):
        if value:
            setattr(self.context, 'mobile_navigation', value)
        elif getattr(self.context, 'mobile_navigation', None) is not None:
            del self.context.mobile_navigation