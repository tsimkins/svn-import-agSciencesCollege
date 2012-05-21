from zope.interface import implements, Interface
from Products.Five import BrowserView
from Products.CMFCore.utils import getToolByName
from Acquisition import aq_acquire, aq_inner, aq_chain
from agsci.blognewsletter.content.interfaces import IBlog
from plone.memoize.view import memoize
from AccessControl import ClassSecurityInfo
from Products.CMFCore import permissions
from zope.security import checkPermission
from zope.security.interfaces import NoInteraction
from DateTime import DateTime
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.registry.interfaces import IRegistry
import premailer
from BeautifulSoup import BeautifulSoup
from zope.component import getUtility, getMultiAdapter
from agsci.blognewsletter.browser.interfaces import *
from zope.component import getUtility
from plone.i18n.normalizer.interfaces import IIDNormalizer
import re
from plone.registry import field
from plone.registry.record import Record
from plone.registry.registry import Registry
from urllib import urlencode
from urlparse import urljoin

"""
    Interface Definitions
"""

class TagsView(BrowserView):

    implements(ITagsView)

    @property
    def normalizer(self):
        return getUtility(IIDNormalizer)

    def page_title(self):
        tags = []
        for t in self.getTags():
            for rt in self.tags:
                if self.normalizer.normalize(t) == rt:
                    tags.append(t)

        if len(tags) > 1:
            plural = 's'
        else:
            plural = ''
            
        return '%s (Tag%s: %s)' % (self.context_state.object_title(), plural, ', '.join(tags))
    
    def publishTraverse(self, request, name):
        if name:
            self.tags = [name]
        self.original_context = self.context
        self.context = self.getTagRoot()

        return self

    def getTagRoot(self):
        # If we're a Blog object, reset the context to the default page
        if self.context.portal_type == 'Blog':
            default_page_id = self.context.getDefaultPage()
            if default_page_id in self.context.objectIds():
               return self.context[default_page_id]
        return self.context

    @memoize
    def getTags(self):

        try:
            selected_tags = self.tags
        except AttributeError:
            selected_tags = []

        available_tags = {}

        for i in aq_chain(self.context):
            if IBlog.providedBy(i):
                for t in sorted(i.available_public_tags):
                    available_tags[self.normalizer.normalize(t)] = t
                break

        if not available_tags and self.context.portal_type == 'Topic':
            for i in self.context.queryCatalog():
                if i.public_tags:
                    for t in i.public_tags:
                        available_tags[self.normalizer.normalize(t)] = t

        item_tags = []

        for t in selected_tags:
            normal_tag = self.normalizer.normalize(t)
            if available_tags.get(normal_tag):
                item_tags.append(available_tags.get(normal_tag))
                
        return item_tags


class NewsletterView(BrowserView):

    implements(INewsletterView)

    index = ViewPageTemplateFile('templates/newsletter_view.pt')
    
    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.currentDate = DateTime()

    @property
    def canEdit(self):
        try:
            return checkPermission('cmf.ModifyPortalContent', self.context)
        except NoInteraction:
            return False

    @property
    def portal_state(self):
        return getMultiAdapter((self.context, self.request), name=u'plone_portal_state')

    @property
    def anonymous(self):
        return self.portal_state.anonymous()

    def getBodyText(self):
        return self.context.getBodyText()

    def tag(self, obj, css_class='tileImage', scale='thumb'):
        context = aq_inner(obj)
        field = context.getField(IMAGE_FIELD_NAME)
        titlef = context.getField(IMAGE_CAPTION_FIELD_NAME)
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
            folderContents = self.context.queryCatalog(batch=True, **contentFilter)
        else:
            folderContents = self.context.getFolderContents(contentFilter, batch=True)

        return folderContents   

    @property
    def registry(self):
        return getUtility(IRegistry)

    def getConfig(self,  key=''):
        try:
            value = self.registry.records[self.getRegistryKey()].value.get(key)

            if key in ['spotlight', 'enabled']:
                if not isinstance(value, list):
                    value = [value]
                    
                contents_uid = set([x.UID for x in self.folderContents()])
    
                return list(contents_uid.intersection(set(value)))
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
        return self.folderContents(contentFilter={'UID' : non_spotlight_uids})    

    def getSpotlightItems(self):
        return self.folderContents(contentFilter={'UID' : self.getSpotlightUID()})

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
        
        # Fix URLs
        
        for a in soup.findAll('a'):
            try:
                href = a['href']
            except KeyError:
                continue

            contents = a.renderContents().strip()

            if not href.startswith('http') and not href.startswith('mailto'):
                a['href'] = urljoin(item.getURL(), href)

            if not contents.startswith('http') and not href.startswith('mailto') and a.get('id') != "parent-fieldname-image":
                a.append("( <strong>%s</strong> )" % a['href'])

            elif '@' not in contents and href.startswith('mailto'):
                a.append("( <strong>%s</strong> )" % a['href'].replace('mailto:', ''))
   
            else:
                a['class'] = 'standalone'

        html = soup.prettify()
        html = html.replace('The external news article is:', 'Full article:') # If there's a news item article link        

        return html
        
    def logo_tag(self):
        # borrowed from plone.app.layout.viewlets.common.LogoViewlet
        bprops = self.portal.restrictedTraverse('base_properties', None)
        if bprops is not None:
            logoName = bprops.logoName
        else:
            logoName = 'logo.png'

        return self.portal.restrictedTraverse(logoName).tag()

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

    def getUTM(self, source=None, medium=None, campaign=None, content=None):
        data = {}

        if source:
            data["utm_source"] = source

        if medium:
            data["utm_medium"] = medium

        if campaign:
            data["utm_campaign"] = campaign

        if content:
            data["utm_content"] = content

        return urlencode(data)

    def __call__(self):
    
        html = self.render()
        html = html.replace('&nbsp;', ' ')
    
        soup = BeautifulSoup(html)
        
        for img in soup.findAll('img', {'class' : 'leadimage'}):
            img['hspace'] = 8
            img['vspace'] = 8


        if self.anonymous:
            utm  = self.getUTM(source='newsletter', medium='email', campaign=self.newsletter_title);
    
            for a in soup.findAll('a'):
                if '?' in a['href']:
                    a['href'] = '%s&%s' % (a['href'], utm) 
                else:
                    a['href'] = '%s?%s' % (a['href'], utm)            

        html = premailer.transform(soup.prettify())

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
     
