from zope.interface import implements, Interface
from Products.Five import BrowserView
from Products.CMFCore.utils import getToolByName
from Acquisition import aq_acquire, aq_inner, aq_chain
from Products.agCommon.browser.views import FolderView
from agsci.subsite.content.interfaces import IBlog
from plone.memoize.view import memoize

"""
    Interface Definitions
"""

from zope.component import getUtility
from plone.i18n.normalizer.interfaces import IIDNormalizer

class IBlogNewsView(Interface):
    """
    blog news view interface
    """

    def test():
        """ test method"""

class ITagsView(Interface):
    """
    tags view interface
    """

    def test():
        """ test method"""

class BlogNewsView(FolderView):
    """
    blog browser view
    """
    implements(IBlogNewsView)
    
    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.months = []
        
        blog = None

        for i in aq_chain(self.context):
            if IBlog.providedBy(i):
                blog = i
                break

        if blog and blog.getDefaultPage() and blog.getDefaultPage() in blog.objectIds():
            listing = blog[blog.getDefaultPage()]
        else:
            return None

        current_year = self.context.getId()
        
        if current_year not in [str(x) for x in range(1900,3000)]:
            return None

        year_query = listing.buildQuery()
        
        year_query['effective'] = { 'query' : ['%s-01-01' % current_year, '%s-12-31' % current_year],  'range': 'minmax' }
        year_query['sort_on'] = 'effective'
        year_query['sort_order'] = 'reverse'
        
        year_results = self.portal_catalog.searchResults(year_query)
        
        month_format = '%B %Y'
        
        months = {}

        for i in year_results:

            effective_date = i.effective
            month = effective_date.strftime('%Y-%m')
            month_id = effective_date.strftime('%m')
            
            if month_id in self.context.objectIds():
                link_month_url = self.context[month_id].absolute_url()
            else:
                link_month_url = None

            if not months.get(month):
                months[month] = {'id' : effective_date.strftime(month_format).lower().replace(' ', '-'), 
                                    'label' : effective_date.strftime(month_format), 'items' : [],
                                    'link_month_url' : link_month_url }

            months[month]['items'].append(i)

        for m in reversed(sorted(months.keys())):
            self.months.append(months[m])

    def getBodyText(self):
        return self.context.getBodyText()

    @property
    def portal_catalog(self):
        return getToolByName(self.context, 'portal_catalog')

    @property
    def portal(self):
        return getToolByName(self.context, 'portal_url').getPortalObject()

class TagsView(FolderView):

    implements(ITagsView)

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.tags = []

    @property
    def portal_catalog(self):
        return getToolByName(self.context, 'portal_catalog')

    @property
    def normalizer(self):
        return getUtility(IIDNormalizer)

    def page_title(self):
        tags = []
        for t in self.getTags():
            for rt in self.tags:
                if self.normalizer.normalize(t) == rt:
                    tags.append(t)

        if len(tags) > 1:
            plural = 's'
        else:
            plural = ''
            
        return '%s (Tag%s: %s)' % (self.context_state.object_title(), plural, ', '.join(tags))
    
    def publishTraverse(self, request, name):
        if name:
            if '|' in name:
                self.tags = sorted(name.split('|'))
            else:
                self.tags = [name]
        else:
            self.tags = []

        self.original_context = self.context
        self.context = self.getTagRoot()

        return self

    def getTagRoot(self):
        # If we're a Blog object, reset the context to the default page
        if self.context.portal_type == 'Blog':
            default_page_id = self.context.getDefaultPage()
            if default_page_id in self.context.objectIds():
               return self.context[default_page_id]
        return self.context

    @memoize
    def getTags(self):

        available_tags = {}
        inside_blog = False
        
        for i in aq_chain(self.context):
            if IBlog.providedBy(i):
                inside_blog = True
                for t in sorted(i.available_public_tags):
                    available_tags[self.normalizer.normalize(t)] = t
                break

        if not available_tags and self.context.portal_type == 'Topic':
            for i in self.context.queryCatalog():
                if i.public_tags:
                    for t in i.public_tags:
                        available_tags[self.normalizer.normalize(t)] = t
        elif not inside_blog:
            for t in self.portal_catalog.uniqueValuesFor('Tags'):
                available_tags[self.normalizer.normalize(t)] = t

        item_tags = []

        for t in self.tags:
            normal_tag = self.normalizer.normalize(t)
            if available_tags.get(normal_tag):
                item_tags.append(available_tags.get(normal_tag))

        return item_tags

    def getFolderContents(self):
        inside_blog = False
        
        for i in aq_chain(self.context):
            if IBlog.providedBy(i):
                inside_blog = True

        if inside_blog:
            return []
        else:
            search_tags = []
            for t in self.portal_catalog.uniqueValuesFor('Tags'):
                if self.normalizer.normalize(t) in self.tags:
                    search_tags.append(t)
            if not search_tags:
                return []
            else:
                return self.portal_catalog.searchResults({'Tags' : search_tags, 'path' : '/'.join(self.context.getPhysicalPath())})
