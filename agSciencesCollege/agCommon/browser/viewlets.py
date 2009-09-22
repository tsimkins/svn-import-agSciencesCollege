from zope.component import getMultiAdapter
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.app.layout.viewlets.common import ViewletBase
from AccessControl import getSecurityManager
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import safe_unicode
from cgi import escape
from Acquisition import aq_acquire
from zope.component import getMultiAdapter
from AccessControl import getSecurityManager

class TopNavigationViewlet(ViewletBase):   
	index = ViewPageTemplateFile('templates/topnavigation.pt')

	def update(self):
		context_state = getMultiAdapter((self.context, self.request),
                                        name=u'plone_context_state')
                                        
		try:
			topMenu = aq_acquire(self.context, 'top-menu')
		except AttributeError:
			topMenu = 'topnavigation'
		
		self.topnavigation = context_state.actions().get(topMenu, None)

class RightColumnViewlet(ViewletBase):   
	index = ViewPageTemplateFile('templates/rightcolumn.pt')

	def update(self):
		self.portal_state = getMultiAdapter((self.context, self.request),
											name=u'plone_portal_state')
		self.anonymous = self.portal_state.anonymous()

class AddThisViewlet(ViewletBase):   
	index = ViewPageTemplateFile('templates/addthis.pt')

	def update(self):
		self.portal_state = getMultiAdapter((self.context, self.request),
											name=u'plone_portal_state')
		self.anonymous = self.portal_state.anonymous()
		

class TitleViewlet(ViewletBase):
	
	def update(self):
		self.portal_state = getMultiAdapter((self.context, self.request),
											name=u'plone_portal_state')
		self.context_state = getMultiAdapter((self.context, self.request),
											 name=u'plone_context_state')
		self.page_title = self.context_state.object_title
		self.portal_title = self.portal_state.portal_title
		
	def index(self):
	
		try:
			site_title = aq_acquire(self.context, 'site_title')
			org_title = "Penn State College of Ag Sciences"
		except AttributeError:
			site_title = self.portal_title()
			org_title = "Penn State University"
	
		portal_title = safe_unicode(site_title)
		page_title = safe_unicode(self.page_title())
		if page_title == portal_title:
			return u"<title>%s &mdash; %s</title>" % (escape(portal_title), escape(org_title))
		else:
			return u"<title>%s &mdash; %s &mdash; %s</title>" % (
				escape(safe_unicode(page_title)),
				escape(safe_unicode(portal_title)),
				escape(safe_unicode(org_title)))

class KeywordsViewlet(ViewletBase):
	
	index = ViewPageTemplateFile('templates/keywords.pt')
	
	def update(self):

		super(KeywordsViewlet, self).update()
		
		context_state = getMultiAdapter((self.context, self.request),
		name=u'plone_context_state')
		tools = getMultiAdapter((self.context, self.request), name=u'plone_tools')
		
		sm = getSecurityManager()
		
		self.user_actions = context_state.actions().get('user', None)
		
		plone_utils = getToolByName(self.context, 'plone_utils')
		
		self.getIconFor = plone_utils.getIconFor
		
		self.anonymous = self.portal_state.anonymous()
