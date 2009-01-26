from zope.component import getMultiAdapter
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.app.layout.viewlets.common import ViewletBase
from AccessControl import getSecurityManager
from Products.CMFCore.utils import getToolByName


class TopNavigationViewlet(ViewletBase):   
	index = ViewPageTemplateFile('templates/topnavigation.pt')

	def update(self):
		context_state = getMultiAdapter((self.context, self.request),
                                        name=u'plone_context_state')
		self.topnavigation = context_state.actions().get('topnavigation', None)
