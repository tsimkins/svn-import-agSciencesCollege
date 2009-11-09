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

class ILinkButton(IPortletDataProvider):

    items = schema.TextLine(title=_(u'Link Button Set Id'),
                       description=_(u'The id of the link button set in portal_actions'),
                       required=True)

class Assignment(base.Assignment):
    implements(ILinkButton)

    items = ""

    def __init__(self, items=items):
        self.items = items
        
    @property
    def title(self):
        return "Link Buttons"


class Renderer(base.Renderer):
    _template = ViewPageTemplateFile('templates/linkbutton.pt')

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
        
        self.linkButtons = context_state.actions().get(self.data.items, None)
        
    def render(self):
        return xhtml_compress(self._template())

    @property
    def available(self):
        return True


class AddForm(base.AddForm):
    form_fields = form.Fields(ILinkButton)
    label = _(u"Add Link Button Portlet")
    description = _(u"This portlet displays link buttons configured in portal_actions.")

    def create(self, data):
        return Assignment(items=data.get('items', ""))

class EditForm(base.EditForm):
    form_fields = form.Fields(ILinkButton)
    label = _(u"Edit Link Button Portlet")
    description = _(u"This portlet displays link buttons configured in portal_actions.")
