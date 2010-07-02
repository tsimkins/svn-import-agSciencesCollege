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
from Products.CMFCore.utils import getToolByName

class IPerson(IPortletDataProvider):

    header = schema.TextLine(
        title=_(u"Portlet header"),
        description=_(u"Title of the rendered portlet"),
        required=True)

    show_header = schema.Bool(
        title=_(u"Show portlet header"),
        description=_(u""),
        required=True,
        default=False)

    people = schema.TextLine(
        title=_(u"Person id(s)"),
        description=_(u"The id(s) of the person to show"),
        required=True)

    show_address = schema.Bool(
        title=_(u"Show office address"),
        description=_(u""),
        required=True,
        default=False)

    show_image = schema.Bool(
        title=_(u"Show person image"),
        description=_(u""),
        required=True,
        default=False)

    hide = schema.Bool(
        title=_(u"Hide portlet"),
        description=_(u"Tick this box if you want to temporarily hide "
                      "the portlet without losing your text."),
        required=True,
        default=False)

class Assignment(base.Assignment):

    implements(IPerson)

    header = ""
    show_header = False
    people = ""
    show_address = False
    show_image = False
    hide = False

    def __init__(self, header=u"", show_header=False, people=people, show_address=False, show_image=False, hide=False):
        self.header = header
        self.show_header = show_header
        self.people = people
        self.show_address = show_address
        self.show_image = show_image
        self.hide = hide
                
    @property
    def title(self):
        if self.header:
            return self.header
        else:
            return "Person Portlet"


class Renderer(base.Renderer):
    _template = ViewPageTemplateFile('templates/person.pt')

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
        
        catalog = getToolByName(context, 'portal_catalog')
        
        peopleList = self.data.people.replace(' ', '').split(",")
        
        self.people = []
        
        search_results = catalog.searchResults({'portal_type' : 'FSDPerson', 'id' : peopleList })
        
        for id in peopleList:
            for r in search_results:
                if r.id == id:
                    self.people.append(r)
      
    def render(self):
        return xhtml_compress(self._template())

    @property
    def available(self):
        return not self.data.hide and self.people


class AddForm(base.AddForm):
    form_fields = form.Fields(IPerson)
    label = _(u"Add Person Portlet")
    description = _(u"This portlet displays information for FSDPerson objects.")

    def create(self, data):
        return Assignment(**data)

class EditForm(base.EditForm):
    form_fields = form.Fields(IPerson)
    label = _(u"Edit Person Portlet")
    description = _(u"This portlet displays information for FSDPerson objects.")
