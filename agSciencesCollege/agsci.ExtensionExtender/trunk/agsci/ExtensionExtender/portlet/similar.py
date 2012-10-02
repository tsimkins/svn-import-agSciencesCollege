from zope import schema
from zope.component import getMultiAdapter
from zope.formlib import form
from zope.interface import implements
from plone.memoize.compress import xhtml_compress

from plone.app.portlets.portlets import base
from plone.memoize.instance import memoize
from plone.portlets.interfaces import IPortletDataProvider
from plone.app.portlets.cache import render_cachekey

from Acquisition import aq_acquire, aq_inner, aq_chain
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFPlone import PloneMessageFactory as _
from Products.CMFCore.utils import getToolByName
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm
from zope.schema.interfaces import IVocabularyFactory

from zope.component import getUtility

from DateTime import DateTime

class TypesVocabulary(object):
    """Vocabulary factory for cache timeouts.
    """
    implements(IVocabularyFactory)

    def __call__(self, context):
        return SimpleVocabulary([
            SimpleTerm('News Item', title="News Item"),
            SimpleTerm('Event', title="Event"),
            SimpleTerm('Person', title="FSDPerson"),
        ])

TypesVocabularyFactory = TypesVocabulary()

class ISimilar(IPortletDataProvider):

    header = schema.TextLine(
        title=_(u"Portlet header"),
        description=_(u"Title of the rendered portlet"),
        required=True)

    show_header = schema.Bool(
        title=_(u"Show portlet header"),
        description=_(u""),
        required=False,
        default=False)

    query_portal_type = schema.Choice(
            title=_(u"heading_query_portal_type",
                default=u"Content Types"),
            description=_(u"description_query_portal_type",
                default=u"Content types to include"),
            required=False,
            vocabulary='agsci.ExtensionExtender.portlet.similar.types'
    )
    
    query_counties = schema.Bool(
        title=_(u"Search Counties"),
        description=_(u""),
        required=False,
        default=False)

    query_programs = schema.Bool(
        title=_(u"Search Programs"),
        description=_(u""),
        required=False,
        default=False)


    query_topics = schema.Bool(
        title=_(u"Search Topics"),
        description=_(u""),
        required=False,
        default=False)
        
    query_subtopics = schema.Bool(
        title=_(u"Search Subtopics"),
        description=_(u""),
        required=False,
        default=False)
        
    query_title = schema.Bool(
        title=_(u"Search Title"),
        description=_(u""),
        required=False,
        default=False)

    limit = schema.Int(
        title=_(u"Limit"),
        description=_(u"Specify the maximum number of items to show in the "
                      u"portlet."),
        required=True,
        default=10)

    show_dates = schema.Bool(
        title=_(u"Show dates"),
        description=_(u""),
        required=False,
        default=True)


class Assignment(base.Assignment):

    implements(ISimilar)

    header = u""
    show_header = False
    query_portal_type = None
    query_counties = False
    query_programs = False
    query_topics = False
    query_subtopics = False
    query_title = False
    limit = 10
    show_dates = True

    def __init__(self, header=header, show_header=show_header, query_portal_type=query_portal_type,
                 query_counties=query_counties, query_programs=query_programs, query_topics=query_topics, 
                 query_subtopics=query_subtopics, query_title=query_title, limit=limit, show_dates=show_dates):
        self.header = header
        self.show_header = show_header
        self.query_portal_type = query_portal_type
        self.query_counties = query_counties
        self.query_programs = query_programs
        self.query_topics = query_topics
        self.query_subtopics = query_subtopics
        self.query_title = query_title
        self.limit = limit
        self.show_dates = show_dates

                
    @property
    def title(self):
        if self.header:
            return self.header
        else:
            return "Similar Items"


class Renderer(base.Renderer):
    _template = ViewPageTemplateFile('templates/similar.pt')

    def __init__(self, *args):
        base.Renderer.__init__(self, *args)

        context = aq_inner(self.context)
        
        self.parent_object = self.context
        
        portal_state = getMultiAdapter((context, self.request), name=u'plone_portal_state')
        self.anonymous = portal_state.anonymous()
        self.portal_url = portal_state.portal_url()
        self.typesToShow = portal_state.friendly_types()

        plone_tools = getMultiAdapter((context, self.request), name=u'plone_tools')
        self.catalog = plone_tools.catalog()
        
        context_state = getMultiAdapter((self.context, self.request), name=u'plone_context_state')

    @property
    def header(self):
        return self.data.header

    @property
    def show_header(self):
        return self.data.show_header

    @property
    def query_portal_type(self):
        return self.data.query_portal_type

    @property
    def query_counties(self):
        return self.data.query_counties

    @property
    def query_programs(self):
        return self.data.query_programs

    @property
    def query_topics(self):
        return self.data.query_topics

    @property
    def query_subtopics(self):
        return self.data.query_subtopics

    @property
    def query_title(self):
        return self.data.query_title

    @property
    def limit(self):
        return self.data.limit

    @property
    def show_dates(self):
        return self.data.show_dates

    def results(self):
        context = aq_inner(self.context)

        similar_query = {'sort_limit' : self.limit + 1}
        
        if self.query_portal_type:
            similar_query['portal_type'] = self.query_portal_type

            if self.query_portal_type in ['Event']:
                similar_query['sort_on'] = 'start'
                similar_query['sort_order'] = 'ascending'
                similar_query['end'] = {'query' : DateTime(), 'range' : 'min'}

            if self.query_portal_type in ['News Item']:
                similar_query['sort_on'] = 'effective'
                similar_query['sort_order'] = 'descending'
                similar_query['effective'] = {'query' : DateTime()-365, 'range' : 'min'}
                
        if self.query_counties and self.context.extension_counties:
            similar_query['Counties'] = self.context.extension_counties

        if self.query_programs and self.context.extension_programs:
            similar_query['Programs'] = self.context.extension_programs

        if self.query_topics and self.context.extension_topics:
            similar_query['Topics'] = self.context.extension_topics

        if self.query_subtopics and self.context.extension_subtopics:
            similar_query['Subtopics'] = self.context.extension_subtopics

        if self.query_title and self.context.Title():
            similar_query['Title'] = self.context.Title()

        all_brains = self.catalog.searchResults(similar_query)

        brains = []

        for b in all_brains:
            if b.UID != self.context.UID():
                brains.append(b)
        
        brains = brains[:self.limit]
        
        return brains

    def render(self):
        return xhtml_compress(self._template())

    @property
    def available(self):
        return self.results()


class AddForm(base.AddForm):
    form_fields = form.Fields(ISimilar)
    label = _(u"Add Similar Portlet")
    description = _(u"This portlet displays tag information for everything in the blog.")

    def create(self, data):
        return Assignment(**data)

class EditForm(base.EditForm):
    form_fields = form.Fields(ISimilar)
    label = _(u"Edit Similar Portlet")
    description = _(u"This portlet displays tag information for everything in the blog.")
