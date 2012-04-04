from zope.interface import implements, Interface
from Products.Five import BrowserView
from Products.CMFCore.utils import getToolByName
from Acquisition import aq_acquire, aq_inner
from collective.contentleadimage.config import IMAGE_FIELD_NAME, IMAGE_CAPTION_FIELD_NAME
from DateTime import DateTime
from urllib import urlencode
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
import premailer
from BeautifulSoup import BeautifulSoup
from zope.component import getUtility, getMultiAdapter
from collective.contentleadimage.leadimageprefs import ILeadImagePrefsForm
import re
from urlparse import urljoin

from AccessControl import ClassSecurityInfo
from Products.CMFCore import permissions

from zope.security import checkPermission

from Products.ZCatalog.CatalogBrains import AbstractCatalogBrain
from Products.CMFPlone.interfaces import IPloneSiteRoot

# For registry

from zope.component import getUtility
from plone.registry.interfaces import IRegistry

from plone.registry.record import Record
from plone.registry.registry import Registry
from plone.registry import field


"""
    Interface Definitions
"""

class IAgendaView(Interface):
    """
    agenda view interface
    """

    def test():
        """ test method"""

class IEventTableView(Interface):
    """
    event table view interface
    """

    def test():
        """ test method"""

class INewsletterView(Interface):

    def test():
        """ test method"""

class ISearchView(Interface):

    def test():
        """ test method"""

class IFolderView(Interface):

    def test():
        """ test method"""

class IAgCommonUtilities(Interface):

    def substituteEventLocation(self):
        pass

    def reorderTopicContents(self):
        pass

    def toMarkdown(self):
        pass

    def getUTM(self):
        pass

    def customBodyClass(self):
        pass


"""
    Class Definitions
"""

class AgCommonUtilities(BrowserView):

    implements(IAgCommonUtilities)

    def substituteEventLocation(self, item):

        try:
            show_event_location = aq_acquire(self.context, 'show_event_location')
        except AttributeError:
            show_event_location = False
                
        if show_event_location and (item.portal_type == 'Event' or item.portal_type == 'TalkEvent') and item.location.strip():
            return item.location.strip()
        else:
            return None        
     
    def reorderTopicContents(self, topicContents, order_by_id=None, order_by_title=None):

        if order_by_id:

            def getId(item):
                if isinstance(item, AbstractCatalogBrain):
                    return item.getId
                else:
                    return item.getId()

            # The +1 applied to both outcomes is so that the index of 0 is not evaluated as false.
            return sorted(topicContents, key=lambda x: getId(x) in order_by_id and (order_by_id.index(getId(x)) + 1) or (len(order_by_id) + 1))
            
            # Reference code
            # The below is slightly faster than the above in cases where order_by_id <= ~5, but the above scales better.
            # I left it in as an explanation of what the above is doing.
            """
            ordered = []
            unordered = []
    
            # Grab all the unordered items
            for item in topicContents:
                if item.getId not in order_by_id:
                    unordered.append(item)
    
            # Grab the ordered items, in order
            for id in order_by_id:
                for item in topicContents:
                    if item.getId == id:
                        ordered.append(item)
    
            # Combine the two lists
            ordered.extend(unordered)
    
            return ordered
            """
        elif order_by_title:
            ordered = []
            uuids = {}

            def getConfig(item):
                if isinstance(item, AbstractCatalogBrain):
                    return item.UID
                else:
                    return item.UID()

            def getTitle(item):
                if isinstance(item, AbstractCatalogBrain):
                    return item.Title
                else:
                    return item.Title()

            for t in order_by_title:
                r = re.compile(t)
  
                # Pull out matching items
                for item in topicContents:
                    if not uuids.get(getConfig(item)) and r.search(getTitle(item)):
                        ordered.append(item)
                        uuids[getConfig(item)] = 1
  
            for item in topicContents:
                if not uuids.get(getConfig(item)):
                    ordered.append(item)
                    uuids[getConfig(item)] = 1

            return ordered
        else:
            return topicContents
        
    def toMarkdown(self, text):
        portal_transforms = getToolByName(self.context, 'portal_transforms')
        return portal_transforms.convert('markdown_to_html', text)
        
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

    def customBodyClass(self):
        context = self.context
        body_classes = []

        if hasattr(context, 'two_column') and context.two_column:
            body_classes.append('custom-two-column')

        if hasattr(context, 'folder_text'):
            body_text = context.folder_text            
        elif hasattr(context, 'getText'):
            body_text = context.getText()
        else:
            body_text = ''
            
        if body_text and '<h2' in body_text.lower() and '<h3' not in body_text.lower():
            body_classes.append('custom-h2-as-h3')

        try:
            custom_class = aq_acquire(self.context, 'custom_class')
            body_classes.extend(['custom-%s' % str(x) for x in custom_class.split()])
        except AttributeError:
            pass

        return ' '.join(body_classes)

#--

class FolderView(BrowserView):

    implements(IFolderView)
    
    def __init__(self, context, request):
        self.context = context
        self.request = request
                                        
    @property
    def show_date(self):
        try:
            show_date = aq_acquire(self.context, 'show_date')
        except AttributeError:
            show_date = False
        
        return show_date

    @property
    def show_image(self):
        try:
            show_image = aq_acquire(self.context, 'show_image')
        except AttributeError:
            show_image = False
        
        return show_image

    @property
    def show_read_more(self):
        try:
            show_read_more = aq_acquire(self.context, 'show_read_more')
        except AttributeError:
            show_read_more = False
        
        return show_read_more

    @property
    def portal_state(self):
        return getMultiAdapter((self.context, self.request), name=u'plone_portal_state')

    @property
    def context_state(self):
        return getMultiAdapter((self.context, self.request),
                                name=u'plone_context_state')

    @property
    def anonymous(self):
        return self.portal_state.anonymous()

    def test(self, a, b, c):
        if a:
            return b
        else:
            return c

    @property
    def prefs(self):
        portal = getUtility(IPloneSiteRoot)
        return ILeadImagePrefsForm(portal)

    def tag(self, obj, css_class='tileImage'):
        context = aq_inner(obj)
        field = context.getField(IMAGE_FIELD_NAME)
        titlef = context.getField(IMAGE_CAPTION_FIELD_NAME)
        if titlef is not None:
            title = titlef.get(context)
        else:
            title = ''
        if field is not None:
            if field.get_size(context) != 0:
                scale = self.prefs.desc_scale_name
                return field.tag(context, scale=scale, css_class=css_class, title=title)
        return ''
            
class SearchView(FolderView):

    implements(ISearchView)
    
    def __init__(self, context, request):
        self.context = context
        self.request = request

    def page_title(self):
        if 'FSDPerson' in self.request.form.get('portal_type', []):
            return 'Search People'
        elif 'Event' in self.request.form.get('portal_type', []):
            return 'Search Events'
        elif 'News Item' in self.request.form.get('portal_type', []):
            return 'Search News'
        else:
            return 'Search'

    def sort_order(self):
        if self.sort_on() in ['created', 'modified', 'effective']:
            return 'descending'
        else:
            return 'ascending'

    def sort_on(self):
        if self.request.form.get('sort_on'):
            return self.request.form['sort_on']
        elif 'FSDPerson' in self.request.form.get('portal_type', []):
            return 'getSortableName'
        elif 'Event' in self.request.form.get('portal_type', []):
            return 'start'
        elif 'News Item' in self.request.form.get('portal_type', []):
            return 'effective'
        else:
            return 'sortable_title'

    def getResults(self):
        now = DateTime()

        filtered_results = []

        use_types_blacklist = self.request.form.get("use_types_blacklist", True) 
        use_navigation_root = self.request.form.get("use_navigation_root", True)

        results = self.context.queryCatalog(REQUEST=self.request,use_types_blacklist=use_types_blacklist, use_navigation_root=use_navigation_root)
        for r in results:
            if self.anonymous and r.portal_type == 'Event' and r.end < now:
                continue
            filtered_results.append(r)
        return filtered_results

class NewsletterView(AgCommonUtilities):

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
        elif self.context.portal_type == 'Topic':
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
        
    def getHTML(self, item):
    
        text = item.getObject().newsletter_full_view_item()
        soup = BeautifulSoup(text)

        # Remove "#tags" div
        for t in soup.findAll("div", attrs={'class' : re.compile('public-tags')}):
            t.extract()
        
        # Fix URLs
        
        for a in soup.findAll('a'):
            href = a['href']
            contents = a.renderContents().strip()

            if not href.startswith('http') and not href.startswith('mailto'):
                a['href'] = urljoin(item.getURL(), href)

            if not contents.startswith('http') and not href.startswith('mailto') and a.get('id') != "parent-fieldname-leadImage":
                a.append("( <strong>%s</strong> )" % a['href'])

            elif '@' not in contents and href.startswith('mailto'):
                a.append("( <strong>%s</strong> )" % a['href'].replace('mailto:', ''))
   
            else:
                a['class'] = 'standalone'

        html = soup.prettify()
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

class AgendaView(FolderView):
    """
    agenda browser view
    """
    implements(IAgendaView)
    
    def __init__(self, context, request):
        self.context = context
        self.request = request
        
        self.month_agenda = []
        self.day_agenda = []
        
        site_properties = getToolByName(self.context, 'portal_properties').get("site_properties")
        day_format = site_properties.localTimeFormat
        month_format = '%B %Y'

        days = {}
        months = {}

        # Set the 'agenda_view_day' property in the ZMI to show the agenda by
        # days rather than by month.  It's not worth having a separate view,
        # since it will be a very small minority of use cases.

        try:
            if aq_acquire(self.context, 'agenda_view_day'):
                self.show_days = True
        except AttributeError:
            self.show_days = False
            
        events = []
        folder_path = ""
        
        self.here_url = self.context.absolute_url()
        
        if self.context.portal_type == 'Topic':
            try:
                events = self.context.queryCatalog()
            except AttributeError:
                # We don't like a relative path here for some reason.
                # Until we figure it out, fall through and just do the default query.
                # That should work in most cases.
                parent_physical_path = list(self.context.getPhysicalPath())
                parent_physical_path.pop()
                folder_path = '/'.join(parent_physical_path)
                pass
            
            # If we're a collection (Topic), we may be a default page.  Figure out
            # if we're the default page, and if so, set the here_url to our parent.
            parent = self.context.getParentNode()
            if self.context.id == parent.getDefaultPage():
                self.here_url = parent.absolute_url()
            
        if not events:
            catalog = getToolByName(self.context, 'portal_catalog')
            
            if not folder_path:
                folder_path = '/'.join(self.context.getPhysicalPath())
                                
            events = catalog.searchResults({'portal_type' : ['Event', 'TalkEvent'],
                                            'path' : {'query': folder_path, 'depth' : 4},
                                            'start' : {'query' : DateTime(), 'range' : 'min'},
                                            'sort_on' : 'start' })
        for e in events:
        
            if e.portal_type == 'Event' or e.portal_type == 'TalkEvent':
                event_start = e.start
                month = event_start.strftime('%Y-%m')
                day = event_start.strftime('%Y-%m-%d')
                
                if not months.get(month):
                    months[month] = {'id' : event_start.strftime(month_format).lower().replace(' ', '-'), 
                                     'label' : event_start.strftime(month_format), 'items' : []}
    
                if not days.get(day):
                    days[day] = {'id' : event_start.strftime(day_format).lower().replace(' ', '-'),
                                 'label' : event_start.strftime(day_format), 'items' : []}
                                    
                months[month]['items'].append(e)
                days[day]['items'].append(e)                

        for m in sorted(months.keys()):
            self.month_agenda.append(months[m])

        for d in sorted(days.keys()):
            self.day_agenda.append(days[d])
            
        if self.show_days:
            self.month_agenda = self.day_agenda
            

    def getBodyText(self):
        return self.context.getBodyText()

    @property
    def portal_catalog(self):
        return getToolByName(self.context, 'portal_catalog')

    @property
    def portal(self):
        return getToolByName(self.context, 'portal_url').getPortalObject()


class EventTableView(AgendaView):
    """
    agenda browser view
    """
    implements(IEventTableView)


class HomepageView(FolderView):

    implements(IFolderView)

    @property
    def hasDescriptionOrText(self):
        if self.hasDescription or self.hasText:
            return True
        else:
            return False

    @property
    def hasDescription(self):
        if self.context.Description():
            return True
        else:
            return False

    @property
    def hasText(self):
        if self.context.getText():
            return True
        else:
            return False
