from zope.interface import implements, Interface

from Products.Five import BrowserView
from Products.CMFCore.utils import getToolByName

from collective.nutritionfacts import nutritionfactsMessageFactory as _


class IJobPageviews(Interface):
    
    pass

class JobPageviews(BrowserView):

    implements(IJobPageviews)

    def __init__(self, context, request):
        self.context = context
        self.request = request

    @property
    def portal_catalog(self):
        return getToolByName(self.context, 'portal_catalog')

    @property
    def portal(self):
        return getToolByName(self.context, 'portal_url').getPortalObject()
        
    def __call__(self):
        request = self.context.REQUEST
        response =  request.response
        response.setHeader('Content-Type', 'text/tab-separated-values')
        response.setHeader('Content-Disposition', 'attachment; filename="agsci_job_pageviews.tsv"')
        pageviews = self.context.getPageviewsReport()
        return "\n".join(["\t".join(x) for x in pageviews])

