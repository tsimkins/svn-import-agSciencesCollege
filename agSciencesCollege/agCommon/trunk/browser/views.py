from zope.interface import implements, Interface
from zope.app.component.hooks import getSite
from Products.Five import BrowserView
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import normalizeString, safe_unicode
from Acquisition import aq_acquire, aq_inner, aq_base
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
from plone.memoize.instance import memoize

from AccessControl import ClassSecurityInfo
from Products.CMFCore import permissions

from zope.security import checkPermission

from Products.ZCatalog.CatalogBrains import AbstractCatalogBrain
from Products.CMFPlone.interfaces import IPloneSiteRoot
from plone.app.workflow.browser.sharing import SharingView, AUTH_GROUP

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
        context = aq_base(self.context)
        body_classes = []

        if hasattr(context, 'two_column') and context.two_column:
            body_classes.append('custom-two-column')

        try:
            if hasattr(context, 'folder_text'):
                body_text = str(context.folder_text)
            elif hasattr(context, 'getText'):
                body_text = str(context.getText())
            else:
                body_text = ''
        except:
            body_text = ''

        if body_text and '<h2' in body_text.lower() and '<h3' not in body_text.lower():
            body_classes.append('custom-h2-as-h3')

        # If 'show_mobile_nav' property is set or
        # we're the homepage at the root of the site, 
        # set class navigation-mobile
        
        try:
            # Explicitly enabled or is a homepage at the root of the site
            if getattr(self.context, 'show_mobile_nav', False) or (self.context.portal_type == 'HomePage' and self.context.getParentNode().portal_type == 'Plone Site'):
                body_classes.append("navigation-mobile")
        except:
            pass

        # If we have a property of 'enable_subsite_nav' set on
        # ourself, or if we're the default page and have it set on our parent
        # object, add a class of 'navigation-subsite'
        parent = self.context.getParentNode()

        try:
            parent_default = parent.getDefaultPage()
        except AttributeError:
            parent_default = ''

        try:
            # Explicitly enabled or is a homepage at the root of the site
            if context.getProperty('enable_subsite_nav', False) or self.context.getId() == parent_default and parent.getProperty('enable_subsite_nav', False):
                body_classes.append("navigation-subsite-root")
        except:
            pass

        try:
            enable_subsite_nav = aq_acquire(self.context, 'enable_subsite_nav')
            if enable_subsite_nav:
                body_classes.append("navigation-subsite")
        except AttributeError:
            pass

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
        files = []

        use_types_blacklist = self.request.form.get("use_types_blacklist", True) 
        use_navigation_root = self.request.form.get("use_navigation_root", True)

        results = self.context.queryCatalog(REQUEST=self.request,use_types_blacklist=use_types_blacklist, use_navigation_root=use_navigation_root)
        for r in results:
            if self.anonymous and r.portal_type == 'Event' and r.end < now:
                continue
            if r.portal_type in ['File']:
                files.append(r)
            else:            
                filtered_results.append(r)
        filtered_results.extend(files)
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

            contents = a.renderContents().strip()

            if not href.startswith('http') and not href.startswith('mailto'):
                a['href'] = urljoin(item.getURL(), href)

            if not contents.startswith('http') and not href.startswith('mailto') and a.get('id') != "parent-fieldname-leadImage":
                a.append(BeautifulSoup("( <strong>%s</strong> )" % a['href']))

            elif '@' not in contents and href.startswith('mailto'):
                a.append(BeautifulSoup("( <strong>%s</strong> )" % a['href'].replace('mailto:', '')))
   
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


        if self.anonymous:
            utm  = self.getUTM(source='newsletter', medium='email', campaign=self.newsletter_title);
    
            for a in soup.findAll('a'):
                if '?' in a['href']:
                    a['href'] = '%s&%s' % (a['href'], utm) 
                else:
                    a['href'] = '%s?%s' % (a['href'], utm)            

        html = premailer.transform(unicode(soup.prettify(), 'utf-8'))

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

        parent = self.context.getParentNode()
        if self.context.id == parent.getDefaultPage():
            self.here_url = parent.absolute_url()
        else:
            self.here_url = self.context.absolute_url()        

        self.month_agenda = []
        self.day_agenda = []
    
    def data(self):
        
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



            
        if self.show_days:

            for d in sorted(days.keys()):
                self.day_agenda.append(days[d])

            return self.day_agenda
        else:

            for m in sorted(months.keys()):
                self.month_agenda.append(months[m])

            return self.month_agenda

            

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

class ModifiedSharingView(SharingView):

    template = ViewPageTemplateFile('templates/sharing.pt')

    @memoize
    def role_settings(self):
        """Get current settings for users and groups for which settings have been made.

        Returns a list of dicts with keys:

         - id
         - title
         - type (one of 'group' or 'user')
         - roles

        'roles' is a dict of settings, with keys of role ids as returned by
        roles(), and values True if the role is explicitly set, False
        if the role is explicitly disabled and None if the role is inherited.
        """

        existing_settings = self.existing_role_settings()
        user_results = self.user_search_results()
        group_results = self.group_search_results()
        
        for g in existing_settings:
            if g['id'] != AUTH_GROUP and g['type'] == 'group':
                g['group_url'] = "%s/@@usergroup-groupmembership?groupname=%s" % (getSite().absolute_url(), g['id'])

        current_settings = existing_settings + user_results + group_results

        # We may be called when the user does a search instead of an update.
        # In that case we must not loose the changes the user made and
        # merge those into the role settings.
        requested = self.request.form.get('entries', None)
        if requested is not None:
            knownroles = [r['id'] for r in self.roles()]
            settings = {}
            for entry in requested:
                roles = [r for r in knownroles
                                if entry.get('role_%s' % r, False)]
                settings[(entry['id'], entry['type'])] = roles

            for entry in current_settings:
                desired_roles = settings.get((entry['id'], entry['type']), None)

                if desired_roles is None:
                    continue
                for role in entry["roles"]:
                    if entry["roles"][role] in [True, False]:
                        entry["roles"][role] = role in desired_roles

        current_settings.sort(key=lambda x: safe_unicode(x["type"])+safe_unicode(x["title"]))

        return current_settings