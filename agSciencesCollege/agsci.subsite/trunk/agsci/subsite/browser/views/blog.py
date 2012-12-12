from zope.interface import implements, Interface
from Products.Five import BrowserView
from Products.CMFCore.utils import getToolByName
from Acquisition import aq_acquire, aq_inner, aq_chain
from Products.agCommon.browser.views import FolderView
from agsci.subsite.content.interfaces import IBlog

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