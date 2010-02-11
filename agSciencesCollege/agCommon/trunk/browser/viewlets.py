from zope.component import getMultiAdapter
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.app.layout.viewlets.common import ViewletBase
from AccessControl import getSecurityManager
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import safe_unicode
from cgi import escape
from Acquisition import aq_acquire, aq_inner
from zope.component import getMultiAdapter
from AccessControl import getSecurityManager
from plone.portlets.interfaces import ILocalPortletAssignable
from plone.app.layout.nextprevious.view import NextPreviousView
from Products.Five.browser.pagetemplatefile import ZopeTwoPageTemplateFile  
from zope.app.component.hooks import getSite
from collective.contentleadimage.browser.viewlets import LeadImageViewlet

homepage_views = ['document_homepage_view', 'document_subsite_view', 'portlet_homepage_view'] 

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
        
        try:
            layout = self.context.getLayout()
        except:
            layout = None
            
        if homepage_views.count(layout) > 0:
            self.isHomePage = True
        else:
            self.isHomePage = False

    def can_manage_portlets(self):

        if not ILocalPortletAssignable.providedBy(self.context):
            return False
        mtool = getToolByName(self.context, 'portal_membership')
        return mtool.checkPermission("Portlets: Manage portlets", self.context)
        

class CenterColumnViewlet(ViewletBase):   
    index = ViewPageTemplateFile('templates/centercolumn.pt')

    def update(self):
        self.portal_state = getMultiAdapter((self.context, self.request),
                                            name=u'plone_portal_state')
        self.anonymous = self.portal_state.anonymous()
        
        try:
            layout = self.context.getLayout()
        except:
            layout = None
            
        if homepage_views.count(layout) > 0:
            self.isHomePage = True
        else:
            self.isHomePage = False

    def can_manage_portlets(self):

        if not ILocalPortletAssignable.providedBy(self.context):
            return False
        mtool = getToolByName(self.context, 'portal_membership')
        return mtool.checkPermission("Portlets: Manage portlets", self.context)

class HomepageImageViewlet(ViewletBase):   
    index = ViewPageTemplateFile('templates/homepageimage.pt')

    def update(self):
        self.portal_state = getMultiAdapter((self.context, self.request),
                                            name=u'plone_portal_state')
        self.anonymous = self.portal_state.anonymous()
        
        try:
            layout = self.context.getLayout()
        except:
            layout = None
            
        if homepage_views.count(layout) > 0:
            self.isHomePage = True
        else:
            self.isHomePage = False

        try:
            self.homepage_h1 = aq_acquire(self.context, 'homepage_h1')
        except AttributeError:
            self.homepage_h1 = None

        try:
            self.homepage_h2 = aq_acquire(self.context, 'homepage_h2')
        except AttributeError:
            self.homepage_h2 = None
            
        # Determine if we should hide breadcrumbs

        try:
            if aq_acquire(self.context, 'hide_breadcrumbs'):
                self.hide_breadcrumbs = True
        except AttributeError:
            if self.homepage_h1 or self.homepage_h2:
                self.hide_breadcrumbs = True
            else:
                self.hide_breadcrumbs = False    


class AddThisViewlet(ViewletBase):   
    index = ViewPageTemplateFile('templates/addthis.pt')

    def update(self):
        self.portal_state = getMultiAdapter((self.context, self.request),
                                            name=u'plone_portal_state')
        self.anonymous = self.portal_state.anonymous()
        
class FooterViewlet(ViewletBase):   
    index = ViewPageTemplateFile('templates/footer.pt')

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

        try:
            org_title = aq_acquire(self.context, 'org_title')
        except AttributeError:
            org_title = org_title

        portal_title = safe_unicode(site_title)
        page_title = safe_unicode(self.page_title())
        org_title = safe_unicode(org_title)

        if not org_title or org_title.lower() == 'none':
            return u"<title>%s &mdash; %s</title>" % (
                escape(safe_unicode(page_title)),
                escape(safe_unicode(portal_title)))
        elif page_title == portal_title:
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
        
class NextPreviousViewlet(ViewletBase, NextPreviousView):
    render = ZopeTwoPageTemplateFile('templates/nextprevious.pt')

class PathBarViewlet(ViewletBase):
    index = ViewPageTemplateFile('templates/path_bar.pt')
        
    def update(self):
        super(PathBarViewlet, self).update()
        
        self.navigation_root_url = self.portal_state.navigation_root_url()
    
        self.is_rtl = self.portal_state.is_rtl()

        breadcrumbs_view = getMultiAdapter((self.context, self.request),
                                           name='breadcrumbs_view')
        self.breadcrumbs = breadcrumbs_view.breadcrumbs()
        
        try:
            layout = self.context.getLayout()
        except:
            layout = None
            
        if homepage_views.count(layout) > 0:
            self.isHomePage = True
        else:
            self.isHomePage = False
        
        # Get the site id
        
        self.site = getSite()['id']

        # Determine if we should hide breadcrumbs
        try:
            if aq_acquire(self.context, 'hide_breadcrumbs'):
                self.hide_breadcrumbs = True
        except AttributeError:
            self.hide_breadcrumbs = False

        try:
            if aq_acquire(self.context, 'homepage_h1'):
                self.hide_breadcrumbs = True
        except AttributeError:
            pass

        try:
            if aq_acquire(self.context, 'homepage_h2'):
                self.hide_breadcrumbs = True
        except AttributeError:
            pass

class LeadImageHeader(LeadImageViewlet):

    def update(self):
    
        # Only show header if we're on a subsite homepage

        context = aq_inner(self.context)
        portal_type = getattr(context, 'portal_type', None)

        try:
            layout = self.context.getLayout()
        except:
            layout = None

        self.showHeader = layout == 'document_subsite_view' and portal_type == 'HomePage'



class RSSViewlet(ViewletBase):
    def update(self):
        super(RSSViewlet, self).update()
        syntool = getToolByName(self.context, 'portal_syndication')
        if syntool.isSyndicationAllowed(self.context):
            self.allowed = True
            context_state = getMultiAdapter((self.context, self.request),
                                            name=u'plone_context_state')
            self.url = '%s/RSS' % context_state.object_url()
            self.page_title = context_state.object_title
        else:
            self.allowed = False

    render = ViewPageTemplateFile('templates/rsslink.pt')