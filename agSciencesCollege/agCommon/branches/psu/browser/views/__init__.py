from zope.interface import implements, Interface
from zope.app.component.hooks import getSite
from Products.Five import BrowserView
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import safe_unicode
from Acquisition import aq_inner
from collective.contentleadimage.config import IMAGE_FIELD_NAME, IMAGE_CAPTION_FIELD_NAME
from DateTime import DateTime
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.component import getUtility, getMultiAdapter
from collective.contentleadimage.leadimageprefs import ILeadImagePrefsForm
from plone.memoize.instance import memoize
from Products.CMFPlone.interfaces import IPloneSiteRoot
from plone.app.workflow.browser.sharing import SharingView, AUTH_GROUP
from Products.agCommon import getContextConfig

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

class ISearchView(Interface):

    def test():
        """ test method"""

class IFolderView(Interface):

    def test():
        """ test method"""


"""
    Class Definitions
"""

class FolderView(BrowserView):

    implements(IFolderView)
    
    def __init__(self, context, request):
        self.context = context
        self.request = request
                                        
    @property
    def show_date(self):
        return getContextConfig(self.context, 'show_date', False)

    @property
    def show_image(self):
        return getContextConfig(self.context, 'show_image', False)

    @property
    def show_read_more(self):
        return getContextConfig(self.context, 'show_read_more', False)

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
        elif 'courses' in self.request.form.get('Subject', []):
            return 'Search Courses'
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

    def getFolderContents(self):
            
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
            catalog = self.portal_catalog
            
            if not folder_path:
                folder_path = '/'.join(self.context.getPhysicalPath())
                                
            events = catalog.searchResults({'portal_type' : ['Event', 'TalkEvent'],
                                            'path' : {'query': folder_path, 'depth' : 4},
                                            'start' : {'query' : DateTime(), 'range' : 'min'},
                                            'sort_on' : 'start' })
        return events

    def data(self):

        site_properties = getToolByName(self.context, 'portal_properties').get("site_properties")
        day_format = site_properties.localTimeFormat
        month_format = '%B %Y'

        # Set the 'agenda_view_day' property in the ZMI to show the agenda by
        # days rather than by month.  It's not worth having a separate view,
        # since it will be a very small minority of use cases.

        self.show_days = getContextConfig(self.context, 'agenda_view_day', False)

        days = {}
        months = {}
        agenda = []

        events = self.getFolderContents()

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
                agenda.append(days[d])

        else:

            for m in sorted(months.keys()):
                agenda.append(months[m])

        return agenda

            

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

    template = ViewPageTemplateFile('../templates/sharing.pt')

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