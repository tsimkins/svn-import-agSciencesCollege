from zope.component import getMultiAdapter, provideAdapter, ComponentLookupError, getUtility
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.app.layout.viewlets.common import ViewletBase, TableOfContentsViewlet
from AccessControl import getSecurityManager
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import safe_unicode
from cgi import escape
from Acquisition import aq_acquire, aq_inner, aq_base, aq_chain
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
import re
from zope.contentprovider.interfaces import IContentProvider
from zope.interface import Interface
from plone.portlets.interfaces import IPortletManager
from Products.CMFPlone.interfaces.siteroot import IPloneSiteRoot
from agsci.subsite.content.interfaces import ISection, ISubsite
from Products.CMFCore.Expression import Expression, getExprContext


try:
    from agsci.ExtensionExtender.interfaces import IExtensionPublicationExtender
except ImportError:
    class IExtensionPublicationExtender(Interface):
        """
            Placeholder interface
        """

from zope.publisher.interfaces.browser import IBrowserView,IDefaultBrowserLayer

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
        elif ( self.context.getText() or self.context.Description() ) and self.isLayout(views=['document_subsite_view', 'portlet_homepage_view', 'panorama_homepage_view']):
            return True
        else:
            return False

    @property    
    def isFolderFullView(self):
        folder_views = ['folder_full_view_item', 'folder_full_view', 'newsletter_view', 'newsletter_email', 'newsletter_print'] 
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
                portal_url = self.context.portal_url()
                context_url = self.context.absolute_url()
                menu_url = t.get('url')
                urls = [menu_url]
                
                # Handle additional URLs configured in portal_actions
                if t.get('additional_urls'):
                    econtext = getExprContext(self.context)
                    for u in t.get('additional_urls'):
                        try:
                            url_expr = Expression(u)
                            urls.append(url_expr.__call__(econtext))
                        except:
                            pass
                        
                for t_url in urls:
                    # Remove trailing / to normalize
                    if t_url.endswith("/"):
                        t_url = t_url[0:-1]
                    if portal_url.endswith("/"):
                        portal_url = portal_url[0:-1]
                    if context_url.endswith("/"):
                        context_url = context_url[0:-1]
                        
                    if portal_url != t_url and context_url.startswith(t_url):
                        matches.append(menu_url) # Remove trailing slash

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
        
        # Integrate Extension PDF download
        self.downloadPDF = False
        if IExtensionPublicationExtender.providedBy(self.context):
            if hasattr(self.context, 'extension_publication_file') and self.context.extension_publication_file:
                self.downloadPDF = True
                self.pdf_url = '%s/extension_publication_file' % self.context.absolute_url()
            elif hasattr(self.context, 'extension_publication_url') and self.context.extension_publication_url:
                self.downloadPDF = True
                self.pdf_url = self.context.extension_publication_url
            elif hasattr(self.context, 'extension_publication_download') and self.context.extension_publication_download:
                self.downloadPDF = True
                self.pdf_url = '%s/pdf_factsheet' % self.context.absolute_url()

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
            self.footer_copyright_2 = ptool.agcommon_properties.footer_copyright_2
            self.footer_copyright_link_2 = ptool.agcommon_properties.footer_copyright_link_2
        except AttributeError:  
            self.footer_copyright_2 = None
            self.footer_copyright_link_2 = None
      
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

    def getImageInfo(self, context=None):
        image_url = image_mime_type = ''
        
        if not context:
            context = self.context
        
        try:
            leadImage_field = context.getField('leadImage', None)
            image_field = context.getField('image', None)
        except AttributeError:
            leadImage_field = None
            image_field = None
            
        if leadImage_field and leadImage_field.get_size(context) > 0:
            image_url = "%s/leadImage" % context.absolute_url()
            image_mime_type = leadImage_field.getContentType(context)
        elif image_field and image_field.get_size(context) > 0:

            sizes = {}

            if hasattr(image_field, 'sizes') and image_field.sizes:
                sizes = image_field.sizes

            image_url = "%s/image" % context.absolute_url()

            image_mime_type = image_field.getContentType(context)

        return (image_url, image_mime_type)
        

    def isDefaultPage(self):
        # Determine if we're the default page
        
        parent = self.context.getParentNode()
        
        try:
            parent_default_page_id = parent.getDefaultPage()
        except AttributeError:
            parent_default_page_id = ''

        return (self.context.id == parent_default_page_id)
        
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
                
        self.showFBMetadata = True

        self.fb_url = self.context.absolute_url()
        
        try:
            # Remove this page's id from the URL if it's a default page.
            if self.isDefaultPage() and self.context.absolute_url().endswith("/%s" % self.context.id) :
                self.fb_url = self.fb_url[0:-1*(len(self.context.id)+1)]
        except:
            pass
        
        # Assign image URL and mime type
        image_url = image_mime_type = ''
        
        # Look up through the acquisition chain until we hit a Plone site, 
        # Section, or Subsite

        for i in aq_chain(self.context):
            if IPloneSiteRoot.providedBy(i):
                break
            
            (image_url, image_mime_type) = self.getImageInfo(i)
            
            if image_url:
                break
            
        # Fallback
        if not image_url:
            image_url = "%s/social-media-site-graphic.png" % self.context.portal_url()

        (self.fb_image, self.link_mime_type) = (image_url, image_mime_type)
        self.link_metadata_image = self.fb_image
        
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

        # Get the site id
        self.site = getSite().getId()
                
        self.navigation_root_url = self.portal_state.navigation_root_url()
    
        self.is_rtl = self.portal_state.is_rtl()

        breadcrumbs_view = getMultiAdapter((self.context, self.request),
                                           name='breadcrumbs_view')
                                           
        if 'extension.psu.edu' in self.site:
            start_breadcrumbs = 2
        else:
            start_breadcrumbs = 1
        end_breadcrumbs = 2
        total_breadcrumbs = start_breadcrumbs + end_breadcrumbs

        all_breadcrumbs = breadcrumbs_view.breadcrumbs()

        if len(all_breadcrumbs) > (total_breadcrumbs + 1):
            empty = {'absolute_url': None, 'Title': '...', }
            all_breadcrumbs = list(all_breadcrumbs)
            self.breadcrumbs = all_breadcrumbs[0:start_breadcrumbs] + [empty] + all_breadcrumbs[-1*end_breadcrumbs:]
        else:
            self.breadcrumbs = all_breadcrumbs


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
    implements(IViewlet, IContentProvider)

    def __init__(self, context, request, view, manager=None):
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

class ContributorsViewlet(AgCommonViewlet):

    implements(IContentProvider)

    index = ViewPageTemplateFile('templates/contributors.pt')
    
    def update(self):
        psuid_re = re.compile("^[A-Za-z][A-Za-z0-9_]*$") # Using one from FSD
        
        self.people = []
        
        peopleList = [x.strip() for x in self.context.Contributors()]
        portal_catalog = getToolByName(self.context, 'portal_catalog')
        search_results = portal_catalog.searchResults({'portal_type' : 'FSDPerson', 'id' : peopleList })
        
        for id in peopleList:
            found = False

            for r in search_results:
                if r.id == id:

                    obj = r.getObject()
                    job_titles = obj.getJobTitles()

                    self.people.append({'name' : obj.pretty_title_or_id(), 
                                        'title' : job_titles and job_titles[0] or '', 
                                        'url' : obj.absolute_url()})
                    found = True

            if not found and not psuid_re.match(id):
                parts = id.split("|")
                parts.extend(['']*(3-len(parts)))
                (name, title, url) = parts
                
                if '@' in url:
                    url = "mailto:%s" % url
                elif not url.startswith('http'):
                    url = ''
                
                self.people.append({'name' : name, 
                                        'title' : title, 
                                        'url' : url})

class CustomCommentsViewlet(CommentsViewlet):

    def update(self):       
        super(CustomCommentsViewlet, self).update()
        try:
            self.xid = md5(self.context.UID()).hexdigest()
        except AttributeError:
            self.xid = md5(self.context.absolute_url()).hexdigest()


class PortletsBelowViewlet(ViewletBase):
    render = ViewPageTemplateFile('templates/portletsbelowcontent.pt')
        
    def update(self):
        """
        Define everything we want to call in the template
        """
        context_state = getMultiAdapter((self.context, self.request), name=u'plone_context_state')
        self.manageUrl =  '%s/@@manage-portletsbelowcontent' % context_state.view_url()
        
        ## This is the way it's done in plone.app.portlets.manager, so we'll do the same
        mt = getToolByName(self.context, 'portal_membership')
        self.canManagePortlets = mt.checkPermission('Portlets: Manage portlets', self.context)

    def have_portlets(self, view=None):
        """Determine whether a column should be shown.
        """
        portlets = False
        context = aq_inner(self.context)
        layout = getMultiAdapter((context, self.request), name=u'plone_layout')

        for manager_name in self.portletManagers():
            if layout.have_portlets(manager_name, view=view):
                portlets = True
        
        return portlets

    def portletManagers(self):
        managers = []
        for n in range(1,7):
            name = 'ContentWellPortlets.BelowPortletManager%d' % n
            managers.append(name)
        return managers



# provideAdapter for viewlets to be registered in standalone mode

provideAdapter(ContributorsViewlet, adapts=(Interface,IDefaultBrowserLayer,IBrowserView), provides=IContentProvider, name='agcommon.contributors')

provideAdapter(AnalyticsViewlet, adapts=(Interface,IDefaultBrowserLayer,IBrowserView), provides=IContentProvider, name='plone.analytics')
