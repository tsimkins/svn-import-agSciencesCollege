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

from zope.interface import implements
from zope.viewlet.interfaces import IViewlet

from Products.Five.browser import BrowserView

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


class FBLikeViewlet(ViewletBase):   
    index = ViewPageTemplateFile('templates/fblike.pt')

    def update(self):
        self.portal_state = getMultiAdapter((self.context, self.request),
                                            name=u'plone_portal_state')
        self.anonymous = self.portal_state.anonymous()
        
        self.likeurl = escape(safe_unicode(self.context.absolute_url()))

        try:
            layout = self.context.getLayout()
        except:
            layout = None
            
        if homepage_views.count(layout) > 0:
            self.isHomePage = True
        else:
            self.isHomePage = False

        
class FooterViewlet(ViewletBase):   
    index = ViewPageTemplateFile('templates/footer.pt')

    def update(self):
        self.portal_state = getMultiAdapter((self.context, self.request),
                                            name=u'plone_portal_state')
        self.anonymous = self.portal_state.anonymous()

class CustomTitleViewlet(ViewletBase):

    def update(self):
        self.portal_state = getMultiAdapter((self.context, self.request),
                                            name=u'plone_portal_state')
        self.context_state = getMultiAdapter((self.context, self.request),
                                             name=u'plone_context_state')

        self.page_title = self.context_state.object_title
        self.portal_title = self.portal_state.portal_title
    
        try:
            self.site_title = aq_acquire(self.context, 'site_title')
            self.org_title = "Penn State College of Ag Sciences"
        except AttributeError:
            self.site_title = self.portal_title()
            self.org_title = "Penn State University"

        try:
            self.org_title = aq_acquire(self.context, 'org_title')
        except AttributeError:
            self.org_title = org_title
            
        
class TitleViewlet(CustomTitleViewlet):
    
    def index(self):
    
        portal_title = escape(safe_unicode(self.site_title))
        page_title = escape(safe_unicode(self.page_title()))
        org_title = escape(safe_unicode(self.org_title))

        if not org_title or org_title.lower() == 'none':
            return u"<title>%s &mdash; %s</title>" % (
                page_title,
                portal_title)
        elif page_title == portal_title:
            return u"<title>%s &mdash; %s</title>" % (portal_title, org_title)
        else:
            return u"<title>%s &mdash; %s &mdash; %s</title>" % (
                page_title,
                portal_title,
                org_title)


class FBMetadataViewlet(CustomTitleViewlet):
    
    index = ViewPageTemplateFile('templates/fbmetadata.pt')

    def update(self):
    
        super(FBMetadataViewlet, self).update()
    
        portal_title = safe_unicode(self.site_title)
        page_title = safe_unicode(self.page_title())
        org_title = safe_unicode(self.org_title)
        
        if not org_title or org_title.lower() == 'none':
            self.fb_title = page_title
            self.fb_site_name = portal_title
        elif page_title == portal_title:
            self.fb_title = portal_title
            self.fb_site_name = org_title
        else:
            self.fb_title = page_title
            self.fb_site_name = "%s (%s)" % (portal_title, org_title)
                
        #self.fb_title = escape(self.fb_title)
        #self.fb_site_name = escape(self.fb_site_name)
        
        # Leadimage or news image

        self.showFBMetadata = True
        
        try:
            leadImage_field = self.context.getField('leadImage', None)
            image_field = self.context.getField('image', None)
        except AttributeError:
            leadImage_field = None
            image_field = None
            self.showFBMetadata = False
            
        if leadImage_field and leadImage_field.get_size(self.context) > 0:
            self.fb_image = "%s/leadImage_mini" % self.context.absolute_url()
        elif image_field and image_field.get_size(self.context) > 0:
            self.fb_image = "%s/image_mini" % self.context.absolute_url()
        else:
            self.fb_image = "%s/leftnavbg.jpg" % self.context.portal_url()
            
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

class AnalyticsViewlet(BrowserView):
    implements(IViewlet)

    def __init__(self, context, request, view, manager):
        super(AnalyticsViewlet, self).__init__(context, request)
        self.__parent__ = view
        self.context = context
        self.request = request
        self.view = view
        self.manager = manager

    def update(self):
        self.portal_state = getMultiAdapter((self.context, self.request),
                                            name=u'plone_portal_state')
        self.anonymous = self.portal_state.anonymous()

    def render(self):
        """render the agsci webstats snippet"""
        if self.anonymous:
            ptool = getToolByName(self.context, "portal_properties")
            snippet = safe_unicode(ptool.site_properties.webstats_js)
        else:
            snippet = ""
        return snippet

class UnitAnalyticsViewlet(AnalyticsViewlet):

    def render(self):
        """render the unit webstats snippet"""   

        if self.anonymous:
            ptool = getToolByName(self.context, "portal_properties")
            snippet = safe_unicode(ptool.site_properties.getProperty("unit_webstats_js", ""))
        else:
            snippet = ""

        return snippet
        

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