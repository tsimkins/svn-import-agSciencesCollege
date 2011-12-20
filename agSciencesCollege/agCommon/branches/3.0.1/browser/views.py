from zope.interface import implements, Interface

from Products.Five import BrowserView
from Products.CMFCore.utils import getToolByName
from Acquisition import aq_acquire, aq_inner
from collective.contentleadimage.config import IMAGE_FIELD_NAME
from collective.contentleadimage.config import IMAGE_CAPTION_FIELD_NAME
from DateTime import DateTime
from urllib import urlencode
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
import premailer
from BeautifulSoup import BeautifulSoup

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

class INewsletterEmail(Interface):

    def test():
        """ test method"""

class NewsletterView(BrowserView):

    implements(INewsletterView)
    
    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.currentDate = DateTime()

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

class NewsletterEmail(NewsletterView):

    implements(INewsletterEmail)

    def render(self):
        return self.index()
        
    def __call__(self):
    
        html = self.render()
    
        soup = BeautifulSoup(html)
        
        for img in soup.findAll('img', {'class' : 'leadimage'}):
            img['hspace'] = 8
            img['vspace'] = 8
    
        html = premailer.transform(soup.prettify())

        tags = ['dl', 'dt', 'dd']
        
        for tag in tags:
            html = html.replace("<%s" % tag, "<div")
            html = html.replace("</%s" % tag, "</div")
            
        return html
    
class AgendaView(BrowserView):
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


class IAgCommonUtilities(Interface):

    def substituteEventLocation(self):
        pass

    def reorderTopicContents(self):
        pass

    def toMarkdown(self):
        pass

    def getUTM(self):
        pass

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
     
    def reorderTopicContents(self, topicContents, order_by_id):
        # The +1 applied to both outcomes is so that the index of 0 is not evaluated as false.
        return sorted(topicContents, key=lambda x: x.getId in order_by_id and (order_by_id.index(x.getId) + 1) or (len(order_by_id) + 1))
        
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