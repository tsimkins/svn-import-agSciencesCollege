from zope.component import getMultiAdapter
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.app.layout.viewlets.common import ViewletBase
from AccessControl import getSecurityManager
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import safe_unicode
from cgi import escape


class TopNavigationViewlet(ViewletBase):   
	index = ViewPageTemplateFile('templates/topnavigation.pt')

	def update(self):
		context_state = getMultiAdapter((self.context, self.request),
                                        name=u'plone_context_state')
		self.topnavigation = context_state.actions().get('topnavigation', None)


class TitleViewlet(ViewletBase):
	
	def update(self):
		self.portal_state = getMultiAdapter((self.context, self.request),
											name=u'plone_portal_state')
		self.context_state = getMultiAdapter((self.context, self.request),
											 name=u'plone_context_state')
		self.page_title = self.context_state.object_title
		self.portal_title = self.portal_state.portal_title
		
	def index(self):
		portal_title = safe_unicode(self.portal_title())
		page_title = safe_unicode(self.page_title())
		if page_title == portal_title:
			return u"<title>%s &mdash; Penn State University</title>" % (escape(portal_title))
		else:
			return u"<title>%s &mdash; %s &mdash; Penn State University</title>" % (
				escape(safe_unicode(page_title)),
				escape(safe_unicode(portal_title)))
