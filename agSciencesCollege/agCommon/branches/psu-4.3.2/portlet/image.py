from zope import schema
from zope.component import getMultiAdapter
from zope.formlib import form
from zope.interface import implements
from plone.memoize.compress import xhtml_compress

from plone.app.portlets.portlets import base
from plone.memoize.instance import memoize
from plone.portlets.interfaces import IPortletDataProvider
from plone.app.portlets.cache import render_cachekey

from Acquisition import aq_inner
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFPlone import PloneMessageFactory as _

class IImage(IPortletDataProvider):

    header = schema.TextLine(
        title=_(u"Portlet header"),
        description=_(u"Title of the rendered portlet"),
        required=True)

    show_header = schema.Bool(
        title=_(u"Show portlet header"),
        description=_(u""),
        required=True,
        default=False)

    items = schema.Choice(title=_(u'Image Set Id'),
                       description=_(u'The id of the image set in portal_actions'),
                       required=True,
                       vocabulary="agcommon.portlet.portal_actions"
                       )

    show_caption = schema.Bool(
        title=_(u"Show captions for images"),
        description=_(u""),
        required=True,
        default=False)
        
    hide = schema.Bool(
        title=_(u"Hide portlet"),
        description=_(u"Tick this box if you want to temporarily hide the portlet without losing your text."),
        required=True,
        default=False)

class Assignment(base.Assignment):

    implements(IImage)

    header = ""
    show_header = ""
    items = ""
    show_caption = ""
    hide = False

    def __init__(self, header=u"", show_header=u"", items=items, show_caption=show_caption, hide=False, *args, **kwargs):
        base.Assignment.__init__(self, *args, **kwargs)
        self.header = header
        self.show_header = show_header
        self.items = items
        self.show_caption = show_caption
        self.hide = hide
                
    @property
    def title(self):
        if self.header:
            return self.header
        else:
            return "Images"


class Renderer(base.Renderer):
    _template = ViewPageTemplateFile('templates/image.pt')

    def __init__(self, *args):
        base.Renderer.__init__(self, *args)

        context = aq_inner(self.context)
        portal_state = getMultiAdapter((context, self.request), name=u'plone_portal_state')
        self.anonymous = portal_state.anonymous()
        self.portal_url = portal_state.portal_url()
        self.typesToShow = portal_state.friendly_types()

        plone_tools = getMultiAdapter((context, self.request), name=u'plone_tools')
        self.catalog = plone_tools.catalog()
        
        context_state = getMultiAdapter((self.context, self.request), name=u'plone_context_state')
        
        self.images = context_state.actions().get(self.data.items, None)
        
    def render(self):
        return xhtml_compress(self._template())

    @property
    def available(self):
        return self.images and not self.data.hide


class AddForm(base.AddForm):
    form_fields = form.Fields(IImage)
    label = _(u"Add Image Portlet")
    description = _(u"This portlet displays linked images configured in portal_actions.")

    def create(self, data):
        return Assignment(**data)

class EditForm(base.EditForm):
    form_fields = form.Fields(IImage)
    label = _(u"Edit Image Portlet")
    description = _(u"This portlet displays linked images configured in portal_actions.")
