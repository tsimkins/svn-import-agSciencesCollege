from Products.agCommon.browser.utilities import AgCommonUtilities
from AccessControl import ClassSecurityInfo
from Acquisition import aq_acquire, aq_inner
from BeautifulSoup import BeautifulSoup
from collective.contentleadimage.config import IMAGE_FIELD_NAME, IMAGE_CAPTION_FIELD_NAME
from collective.contentleadimage.browser.viewlets import LeadImageViewlet
from DateTime import DateTime
from plone.registry import field
from plone.registry.interfaces import IRegistry
from plone.registry.record import Record
from plone.registry.registry import Registry
from Products.CMFCore import permissions
from Products.CMFCore.utils import getToolByName
from urlparse import urljoin
from zope.component import getUtility, getMultiAdapter
from zope.interface import implements, Interface
from zope.security import checkPermission

import premailer
import re

class INewsletterView(Interface):

    def test():
        """ test method"""

class IEventInvitationView(Interface):

    def test():
        """ test method"""

class NewsletterView(AgCommonUtilities, LeadImageViewlet):

    implements(INewsletterView)
    
    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.currentDate = DateTime()

    @property
    def canEdit(self):
        return checkPermission('cmf.ModifyPortalContent', self.context)

    @property
    def anonymous(self):
        self.portal_state = getMultiAdapter((self.context, self.request), name=u'plone_portal_state')
        return self.portal_state.anonymous()

    def getBodyText(self):
        return self.context.getBodyText()

    def tag(self, obj, css_class='tileImage', scale='thumb'):
        context = aq_inner(obj)
        field = context.getField(IMAGE_FIELD_NAME)
        titlef = context.getField(IMAGE_CAPTION_FIELD_NAME)

        if not field:
            field = context.getField('image')

        if not titlef:
            titlef = context.getField('imageCaption')        
        
        if titlef is not None:
            title = titlef.get(context)
        else:
            title = ''

        if field is not None:
            if field.get_size(context) != 0:
                return field.tag(context, scale=scale, css_class=css_class, title=title, alt=title)
        return ''

    @property
    def portal_catalog(self):
        return getToolByName(self.context, 'portal_catalog')

    @property
    def portal(self):
        return getToolByName(self.context, 'portal_url').getPortalObject()
        
    @property
    def newsletter_title(self):
        try:
            newsletter_title = aq_acquire(self.context, 'newsletter_title')
        except AttributeError:
            newsletter_title = None
        try:
            site_title = aq_acquire(self.context, 'site_title')
        except AttributeError:
            site_title = None
                   
        context_title = self.context.Title();

        if newsletter_title:
            return newsletter_title
        elif site_title:
            return '%s: %s' % (site_title, context_title)
        else:
            return context_title

    def isEnabled(self, item):

        enabled_items = self.getEnabledUID()

        if enabled_items:
            return item.UID in enabled_items
        else:
            return self.anonymous

    def isSpotlight(self, item):

        return item.UID in self.getSpotlightUID()
        
    def showItem(self, item, item_type='enabled'):
        if item_type=='spotlight':
            return self.isSpotlight(item)
        elif self.isEnabled(item):
            return not self.isSpotlight(item)
        else:
            return not self.anonymous

    @property
    def showSummary(self):
        show_summary = self.getConfig('show_summary')
        
        if show_summary == 'yes':
            return True
        elif show_summary == 'no':
            return False
        else:
            return len(self.getEnabledItems()) >= 5

    def folderContents(self, folderContents=[], contentFilter={}):

        if folderContents:
            # Already has folder contents
            pass
        elif self.context.portal_type in ['Topic', 'Newsletter']:
            order_by_title = getattr(self.context, 'order_by_title', None)
            order_by_id = getattr(self.context, 'order_by_id', None)

            folderContents = self.context.queryCatalog(batch=True, **contentFilter)

            if order_by_id or order_by_title:
                folderContents = self.reorderTopicContents(folderContents, order_by_id=order_by_id, order_by_title=order_by_title) 
        else:
            folderContents = self.context.getFolderContents(contentFilter, batch=True)

        return folderContents   

    @property
    def registry(self):
        return getUtility(IRegistry)

    def getSortCriterion(self):
        if self.context.portal_type in ['Topic', 'Newsletter'] and self.context.hasSortCriterion():
            sc = self.context.getSortCriterion()
            if sc.getReversed():
                sort_dir = 'descending'
            else:
                sort_dir = 'ascending'
            return (sc.field, sort_dir)
        else:
            return ('effective', 'descending')
        
    def getConfig(self,  key=''):
        try:
            value = self.registry.records[self.getRegistryKey()].value.get(key)

            if key in ['spotlight', 'enabled']:
                if not isinstance(value, list):
                    value = [value]

                return value
                
                #contents_uid = set([x.UID for x in self.folderContents()])
    
                #return list(contents_uid.intersection(set(value)))
            else:
                return value
            
        except (KeyError, AttributeError):
            return []

    def getEnabledUID(self):
        return self.getConfig(key='enabled')

    def getSpotlightUID(self):
        return self.getConfig(key='spotlight')

    def getAllItems(self):
        return self.folderContents()

    def getEnabledItems(self):
        non_spotlight_uids = list(set(self.getEnabledUID()) - set(self.getSpotlightUID()))
        (sort_on, sort_order) = self.getSortCriterion()
        results = self.portal_catalog.searchResults({'UID' : non_spotlight_uids, 'sort_on' : sort_on, 'sort_order' : sort_order})    

        order_by_title = getattr(self.context, 'order_by_title', None)
        order_by_id = getattr(self.context, 'order_by_id', None)

        if order_by_id or order_by_title:
            results = self.reorderTopicContents(results, order_by_id=order_by_id, order_by_title=order_by_title) 

        return results


    def getSpotlightItems(self):
        (sort_on, sort_order) = self.getSortCriterion()
        return self.portal_catalog.searchResults({'UID' : self.getSpotlightUID(), 'sort_on' : sort_on, 'sort_order' : sort_order})    

    def setConfig(self, enabled=[], spotlight=[], show_summary=[]):
        # Make all spotlight articles enabled
        enabled = list(set(enabled).union(set(spotlight)))
    
        self.registry.records[self.getRegistryKey()] = Record(field.Dict(title=u"Item UIDs"), {'enabled' : enabled, 'spotlight' : spotlight, 'show_summary' : show_summary})
        
    def getRegistryKey(self):
        return 'agsci.newsletter.uid_%s' % self.context.UID()

    def getViewOnline(self):
        parent = self.context.getParentNode()
        if parent.portal_type == 'Blog':
            return parent.absolute_url()
        else:
            return self.context.absolute_url()

    def getHTML(self, item):
    
        text = item.getObject().newsletter_full_view_item()
        soup = BeautifulSoup(text)

        # Remove "#tags" div
        for t in soup.findAll("div", attrs={'class' : re.compile('public-tags')}):
            t.extract()

        # Fix Images
        
        for i in soup.findAll('img'):
            try:
                src = i['src']
            except KeyError:
                continue

            if not src.startswith('http') :
                i['src'] = urljoin(item.getURL(), src)

        
        # Fix URLs
        
        for a in soup.findAll('a'):
            try:
                href = a['href']
            except KeyError:
                continue

            # In lieu of doing default page logic, trim known default pages

            for (default_page, replace_with) in [('/news/latest', '/news'), ('/events/upcoming', '/events'), ('/front-page', '')]:
                if href.endswith(default_page):
                    href = "%s%s" % (href[0:-1*len(default_page)], replace_with)
                    a['href'] = href

            contents = a.renderContents().strip()

            if not href.startswith('http') and not href.startswith('mailto'):
                a['href'] = urljoin(item.getURL(), href)

            if not contents.startswith('http') and not href.startswith('mailto') and a.get('id') != "parent-fieldname-leadImage":
                a.append(BeautifulSoup("( <strong>%s</strong> )" % a['href']))

            elif '@' not in contents and href.startswith('mailto'):
                a.append(BeautifulSoup("( <strong>%s</strong> )" % a['href'].replace('mailto:', '')))
   
            else:
                a['class'] = 'standalone'

        html = repr(soup)
        html = html.replace('The external news article is:', 'Full article:') # If there's a news item article link        

        return html

class NewsletterModify(NewsletterView):

    security = ClassSecurityInfo()
    security.declareProtected(permissions.ModifyPortalContent, '__call__')

    def __call__(self):
        enabled_items = self.request.form.get('enabled_items', [])
        spotlight_items = self.request.form.get('spotlight_items', [])
        show_summary = self.request.form.get('show_summary', 'auto')
        
        if not isinstance(enabled_items, list):
            enabled_items = [enabled_items]

        if not isinstance(spotlight_items, list):
            spotlight_items = [spotlight_items]

        self.setConfig(enabled=enabled_items, spotlight=spotlight_items, show_summary=show_summary)

        self.request.response.redirect(self.context.absolute_url())
        
class NewsletterEmail(NewsletterView):

    implements(INewsletterView)

    def render(self):
        return self.index()
        
    def __call__(self):
    
        html = self.render()
        html = html.replace('&nbsp;', ' ')
    
        soup = BeautifulSoup(html)
        
        for img in soup.findAll('img', {'class' : 'leadimage'}):
            img['hspace'] = 8
            img['vspace'] = 8


        if self.anonymous:
    
            for a in soup.findAll('a'):
                klass = [x.replace('utm_', '') for x in a.get('class', '').split() if x.startswith('utm_')]
                utm_content = None
                
                if klass:
                    utm_content = klass[0]
                    
                utm  = self.getUTM(source='newsletter', medium='email', 
                                   campaign=self.newsletter_title, content=utm_content);

                if '?' in a['href']:
                    a['href'] = '%s&%s' % (a['href'], utm) 
                else:
                    a['href'] = '%s?%s' % (a['href'], utm)            

        html = premailer.transform(unicode(repr(soup), 'utf-8'))

        tags = ['dl', 'dt', 'dd']
        
        for tag in tags:
            html = html.replace("<%s" % tag, "<div")
            html = html.replace("</%s" % tag, "</div")

        html = re.sub('\s+', ' ', html)
        html = html.replace(' </a>', '</a> ')

        return html

class NewsletterPrint(NewsletterView):

    implements(INewsletterView)

    pass

class EventInvitationView(NewsletterView):

    implements(IEventInvitationView)
