from zope.component import getMultiAdapter
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.app.layout.viewlets.common import ViewletBase, TableOfContentsViewlet
from AccessControl import getSecurityManager
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import safe_unicode
from cgi import escape
from Acquisition import aq_acquire, aq_inner, aq_base
from zope.component import getMultiAdapter
from AccessControl import getSecurityManager
from plone.portlets.interfaces import ILocalPortletAssignable
from plone.app.layout.nextprevious.view import NextPreviousView
from Products.Five.browser.pagetemplatefile import ZopeTwoPageTemplateFile  
from zope.app.component.hooks import getSite
from collective.contentleadimage.browser.viewlets import LeadImageViewlet
from plone.app.discussion.browser.comments import CommentsViewlet
from zope.interface import implements
from zope.viewlet.interfaces import IViewlet
from hashlib import md5

from Products.Five.browser import BrowserView

class AgCommonViewlet(ViewletBase):

    def update(self):
        pass

    @property
    def portal_state(self):
        return getMultiAdapter((self.context, self.request),
                                name=u'plone_portal_state')

    @property
    def context_state(self):
        return getMultiAdapter((self.context, self.request),
                                name=u'plone_context_state')

    @property
    def anonymous(self):
        return self.portal_state.anonymous()

    @property
    def homepage_h1(self):
        try:
            return aq_acquire(self.context, 'homepage_h1')
        except AttributeError:
            return None

    @property
    def homepage_h2(self):
        try:
            return aq_acquire(self.context, 'homepage_h2')
        except AttributeError:
            return None

    @property
    def hide_breadcrumbs(self):
        # Determine if we should hide breadcrumbs

        if self.homepage_h1 or self.homepage_h2:
            return True
    
        try:
            return aq_acquire(self.context, 'hide_breadcrumbs')
        except AttributeError:
            return False

    def isLayout(self, views=[]):
        try:
            layout = self.context.getLayout()
        except:
            layout = None
            
        if layout in views:
            return True
        else:
            for v in views:
                if v in self.context.absolute_url():
                    return True
    
            return False

    @property
    def isHomePage(self):
        return self.isLayout(views=['document_homepage_view', 'document_subsite_view', 'portlet_homepage_view', 'panorama_homepage_view'])

    @property
    def showHomepageText(self):
        if self.context.getText() and self.isLayout(views=['document_homepage_view']):
            return True
        elif ( self.context.getText() or self.context.Description ) and self.isLayout(views=['document_subsite_view', 'portlet_homepage_view', 'panorama_homepage_view']):
            return True
        else:
            return False

    @property    
    def isFolderFullView(self):
        folder_views = ['folder_full_view_item', 'folder_full_view'] 
        parent = self.context.getParentNode()
        try:
            default_page = parent.getDefaultPage()
        except AttributeError:
            default_page = None
        
        if default_page and default_page in parent.objectIds():
            try:
                layout = parent[default_page].getLayout()
            except:
                layout = None
        else:
            try:
                layout = parent.getLayout()
            except:
                layout = None
    
        if layout in folder_views:
            return True
        else:
            for v in folder_views:
                if v in self.context.absolute_url():
                    return True
    
            return False
    
    @property
    def showTwoColumn(self):
    
        try:
            layout = self.context.getLayout()
        except:
            layout = None
            
        if layout in ['factsheet_view']:
            return True
        else:
            return False


class PortletViewlet(AgCommonViewlet):

    def can_manage_portlets(self):

        if not ILocalPortletAssignable.providedBy(self.context):
            return False
        mtool = getToolByName(self.context, 'portal_membership')
        return mtool.checkPermission("Portlets: Manage portlets", self.context)


class TopNavigationViewlet(AgCommonViewlet):   
    index = ViewPageTemplateFile('templates/topnavigation.pt')

    def update(self):
                                        
        try:
            topMenu = aq_acquire(self.context, 'top-menu')
        except AttributeError:
            topMenu = 'topnavigation'
            
        self.topnavigation = self.context_state.actions().get(topMenu, None)

        # URL that contains the section
        self.container_url = None

        if self.topnavigation:
            matches = []
    
            for t in self.topnavigation:
                t_url = t.get('url')
                portal_url = self.context.portal_url()
                context_url = self.context.absolute_url()

                # Remove trailing / to normalize
                if t_url.endswith("/"):
                    t_url = t_url[0:-1]
                if portal_url.endswith("/"):
                    portal_url = portal_url[0:-1]
                if context_url.endswith("/"):
                    context_url = context_url[0:-1]
                    
                if portal_url != t_url and context_url.startswith(t_url):
                    matches.append(t_url) # Remove trailing slash

            if matches:
                self.container_url = sorted(matches, key=lambda x:len(x), reverse=True)[0]


class RightColumnViewlet(PortletViewlet):   
    index = ViewPageTemplateFile('templates/rightcolumn.pt')


class CenterColumnViewlet(PortletViewlet):   
    index = ViewPageTemplateFile('templates/centercolumn.pt')


class HomepageTextViewlet(AgCommonViewlet):   
    index = ViewPageTemplateFile('templates/homepagetext.pt')


class HomepageImageViewlet(AgCommonViewlet):   
    index = ViewPageTemplateFile('templates/homepageimage.pt')


class AddThisViewlet(AgCommonViewlet):   
    index = ViewPageTemplateFile('templates/addthis.pt')

    def update(self):

        syntool = getToolByName(self.context, 'portal_syndication')

        self.isSyndicationAllowed = syntool.isSyndicationAllowed(self.context)

        portal_type = getattr(self.context, 'portal_type', None)

        if portal_type == 'FSDPerson':
            self.isPerson = True
        else:
            self.isPerson = False
        
        ptool = getToolByName(self.context, "portal_properties")

        self.hide_addthis = not ptool.agcommon_properties.enable_addthis

        try:
            self.hide_addthis = aq_acquire(self.context, 'hide_addthis')
        except AttributeError:
            pass

        # If in folder_full_view_item, hide it on the individual items.
        if self.isFolderFullView:
            self.hide_addthis = True


class FBLikeViewlet(AgCommonViewlet):   
    index = ViewPageTemplateFile('templates/fblike.pt')

    def update(self):
        self.likeurl = escape(safe_unicode(self.context.absolute_url()))

        
class FooterViewlet(AgCommonViewlet):   
    index = ViewPageTemplateFile('templates/footer.pt')

    def update(self):

        # Get copyright info
        ptool = getToolByName(self.context, "portal_properties")

        self.footer_copyright = ptool.agcommon_properties.footer_copyright
        self.footer_copyright_link = ptool.agcommon_properties.footer_copyright_link
        
        try:
            footerlinks = aq_acquire(self.context, 'footerlinks')
        except AttributeError:
            footerlinks = 'footerlinks'

        self.footerlinks = self.context_state.actions().get(footerlinks, None)
        
class CustomTitleViewlet(AgCommonViewlet):

    def update(self):
        try:
            self.page_title = self.view.page_title
        except AttributeError:
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
            self.org_title = ""
            
        
class TitleViewlet(CustomTitleViewlet):
    
    def index(self):
    
        portal_title = escape(safe_unicode(self.site_title))
        page_title = escape(safe_unicode(self.page_title()))
        org_title = escape(safe_unicode(self.org_title))

        if page_title == portal_title == org_title:
            return u"<title>%s</title>" % (org_title)
        elif org_title == portal_title:
            return u"<title>%s &mdash; %s</title>" % (page_title, org_title)
        elif page_title == portal_title:
            return u"<title>%s &mdash; %s</title>" % (portal_title, org_title)
        elif not org_title or org_title.lower() == 'none':
            return u"<title>%s &mdash; %s</title>" % (
                page_title,
                portal_title)
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
        
        self.fb_url = self.context.absolute_url()
        
        try:
            # Remove this page's id from the URL if it's a default page.
            if self.context.id == self.context.default_page and  self.context.absolute_url().endswith("/%s" % self.context.id) :
                self.fb_url = self.fb_url[0:-1*(len(self.context.id)+1)]
        except:
            pass

        try:
            leadImage_field = self.context.getField('leadImage', None)
            image_field = self.context.getField('image', None)
        except AttributeError:
            leadImage_field = None
            image_field = None
            self.showFBMetadata = False
            
        if leadImage_field and leadImage_field.get_size(self.context) > 0:
            self.fb_image = "%s/leadImage_mini" % self.context.absolute_url()
            self.link_metadata_image = self.fb_image
            self.link_mime_type = leadImage_field.getContentType(self.context)
        elif image_field and image_field.get_size(self.context) > 0:
            self.fb_image = "%s/image_mini" % self.context.absolute_url()
            self.link_metadata_image = self.fb_image
            self.link_mime_type = image_field.getContentType(self.context)
        else:
            self.fb_image = "%s/leftnavbg.jpg" % self.context.portal_url()
            self.link_metadata_image = None
            self.link_mime_type = None

        # FB config
        self.fbadmins = ['100001031380608','9324502','9370853','1485890864']

        try:
            self.fbadmins.extend(aq_acquire(self.context, 'fbadmins'))
        except AttributeError:
            pass
            
        self.fbadmins = ','.join(self.fbadmins)

        try:
            self.fbappid = aq_acquire(self.context, 'fbappid')
        except AttributeError:
            self.fbappid = '374493189244485'

        try:
            self.fbpageid = aq_acquire(self.context, 'fbpageid')
        except AttributeError:
            self.fbpageid = '53789486293'
            

            
class KeywordsViewlet(AgCommonViewlet):
    
    index = ViewPageTemplateFile('templates/keywords.pt')
    
    def update(self):

        super(KeywordsViewlet, self).update()
        
        tools = getMultiAdapter((self.context, self.request), name=u'plone_tools')
        
        sm = getSecurityManager()
        
        self.user_actions = self.context_state.actions().get('user', None)
        
        plone_utils = getToolByName(self.context, 'plone_utils')
        
        self.getIconFor = plone_utils.getIconFor
        
class NextPreviousViewlet(ViewletBase, NextPreviousView):
    render = ZopeTwoPageTemplateFile('templates/nextprevious.pt')

class PathBarViewlet(AgCommonViewlet):
    index = ViewPageTemplateFile('templates/path_bar.pt')
        
    def update(self):
        super(PathBarViewlet, self).update()
        
        self.navigation_root_url = self.portal_state.navigation_root_url()
    
        self.is_rtl = self.portal_state.is_rtl()

        breadcrumbs_view = getMultiAdapter((self.context, self.request),
                                           name='breadcrumbs_view')
        self.breadcrumbs = breadcrumbs_view.breadcrumbs()
        
        # Get the site id
        self.site = getSite()['id']

class LeadImageHeader(LeadImageViewlet, AgCommonViewlet):

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
        

class RSSViewlet(AgCommonViewlet):
    def update(self):
        super(RSSViewlet, self).update()
        syntool = getToolByName(self.context, 'portal_syndication')
        if syntool.isSyndicationAllowed(self.context):
            self.allowed = True
            self.url = '%s/RSS' % self.context_state.object_url()
            self.page_title = self.context_state.object_title
        else:
            self.allowed = False

    render = ViewPageTemplateFile('templates/rsslink.pt')
    
class SiteRSSViewlet(ViewletBase):
    def update(self):
        ptool = getToolByName(self.context, "portal_properties")

        self.show_site_rss = False
        try:
            self.site_rss_title = ptool.agcommon_properties.site_rss_title
            self.site_rss_link = ptool.agcommon_properties.site_rss_link

            if self.site_rss_title and self.site_rss_link:
                self.show_site_rss = True

        except AttributeError:
            # Don't show site RSS
            pass
            
        
    render = ViewPageTemplateFile('templates/site_rss.pt')    

class TableOfContentsViewlet(AgCommonViewlet):

    index = ViewPageTemplateFile('templates/toc.pt')

    def update(self):
        obj = aq_base(self.context)
        getTableContents = getattr(obj, 'getTableContents', None)      

        self.enabled = False

        if getTableContents is not None:
            try:
                self.enabled = getTableContents()
            except KeyError:   
                # schema not updated yet
                self.enabled = False

        if self.isFolderFullView:
            self.enabled = False


class CustomCommentsViewlet(CommentsViewlet):

    def update(self):       
        super(CustomCommentsViewlet, self).update()
        try:
            self.xid = md5(self.context.UID()).hexdigest()
        except AttributeError:
            self.xid = md5(self.context.absolute_url()).hexdigest()
