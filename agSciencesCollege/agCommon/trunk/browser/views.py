from zope.interface import implements, Interface

from Products.Five import BrowserView
from Products.CMFCore.utils import getToolByName
from Acquisition import aq_acquire, aq_inner
from DateTime import DateTime

import pdb

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
                show_days = True
        except AttributeError:
            show_days = False

        if self.context.portal_type == 'Topic':
            events = self.context.queryCatalog()
            
        else:
            catalog = getToolByName(self.context, 'portal_catalog')
            
            folder_path = '/'.join(self.context.getPhysicalPath())
                                
            events = catalog.searchResults({'portal_type' : 'Event', 
                                            'path' : {'query': folder_path, 'depth' : 4},
                                            'start' : {'query' : DateTime(), 'range' : 'min'},
                                            'sort_on' : 'start' })
        for e in events:
        
            if e.portal_type == 'Event':
                event_start = e.start
                month = event_start.strftime('%Y-%m')
                day = event_start.strftime('%Y-%m-%d')
                
                if not months.get(month):
                    months[month] = {'label' : event_start.strftime(month_format), 'items' : []}
    
                if not days.get(day):
                    days[day] = {'label' : event_start.strftime(day_format), 'items' : []}
                                    
                months[month]['items'].append(e)
                days[day]['items'].append(e)                

        for m in sorted(months.keys()):
            self.month_agenda.append(months[m])

        for d in sorted(days.keys()):
            self.day_agenda.append(days[d])
            
        if show_days:
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