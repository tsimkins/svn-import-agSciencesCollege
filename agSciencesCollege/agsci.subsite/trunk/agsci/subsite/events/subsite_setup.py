from Products.CMFCore.utils import getToolByName

from zope.component import getUtility
from zope.component import getMultiAdapter
from zope.app.container.interfaces import INameChooser
import pdb

from plone.portlets.interfaces import IPortletManager, IPortletAssignmentMapping, ILocalPortletAssignmentManager

from plone.portlets.constants import CONTEXT_CATEGORY

from plone.app.portlets.portlets import navigation
from collective.portlet import feedmixer
from plone.portlet.collection import collection

from datetime import datetime

from zLOG import LOG, INFO

from zope.component.interfaces import ComponentLookupError

# wrapper functions for working with portlets. All the adaptors kept confusing me.
def getPortletAssignmentMapping(context, name):
    portlet_manager = getPortletManager(context, name)
    return getMultiAdapter((context, portlet_manager), IPortletAssignmentMapping, context=context)

def getPortletManager(context, name):
    return getUtility(IPortletManager, name=name, context=context)

def getLocalPortletAssignmentManager(context, name):
    portlet_manager = getPortletManager(context, name)
    return getMultiAdapter((context, portlet_manager), ILocalPortletAssignmentManager)
    
# Save the portlet assignment
def saveAssignment(mapping, assignment):
    chooser = INameChooser(mapping)
    mapping[chooser.chooseName(None, assignment)] = assignment

# Write debug messages to log file
def writeDebug(msg):
    LOG('agsci.subsite', INFO, msg)
    
# What we want to happen when we create a subsite
def onSubsiteCreation(subsite, event):

    writeDebug('Beginning post create script.')

    # Get URL tool
    urltool = getToolByName(subsite, 'portal_url')
    
    # Remove top menu
    writeDebug('Removing top menu')
    subsite.manage_addProperty('top-menu', 'none', 'string')

    writeDebug('Creating news folder')
    
    # Create Blog 'news' folder
    if 'news' not in subsite.objectIds():
        subsite.invokeFactory(type_name='Folder', id='news', title='News')
        # All the other goodies get taken care of through the 'Blog' content type

        # Let's put a spotlight subfolder, etc. within the news folder from here.
        # Not all blogs need a spotlight folder, and we tie the spotlight tag to the
        # name of the subsite.
    
        writeDebug('Creating spotlight folder')
    
        news = subsite['news']
    
        # create a folder for spotlight items inside the news folder
        if 'spotlight' not in news.objectIds():
            news.invokeFactory(type_name='Folder', id='spotlight', title='Spotlight')
            
            spotlight_obj = news['spotlight']
            spotlight_obj.setConstrainTypesMode(1) # restrict what this folder can contain
            spotlight_obj.setImmediatelyAddableTypes(['Link','Folder','File','Document'])
            spotlight_obj.setLocallyAllowedTypes(['Link','Folder','File','Document','Topic'])
            spotlight_obj.reindexObject()
            
            writeDebug('Creating recent spotlight topic')
            spotlight_obj.invokeFactory(type_name='Topic', id='recent', title='Spotlight')
            
            smart_obj = spotlight_obj['recent']
            
            spotlight_obj.setDefaultPage('recent')
        
            # Set the criteria for the folder
            path_crit = smart_obj.addCriterion('path','ATPathCriterion')
            path_crit.setValue(subsite.UID()) # Only list items in the current subsite
            path_crit.setRecurse(True)
    
            # Set the criteria for the folder
            tag_crit = smart_obj.addCriterion('Subject','ATSelectionCriterion')
            tag_crit.setValue("spotlight-%s" % subsite.id) # Only list items in the current subsite
        
            sort_crit = smart_obj.addCriterion('sortable_title','ATSortCriterion')
            sort_crit.setReversed(True)
            
            # Create sample spotlight item
            writeDebug('Creating sample spotlight item')
            spotlight_obj.invokeFactory(type_name='Document', id='sample', title='Sample Spotlight Item', description='This is a sample Spotlight Item', text='<p>You may delete this item</p>', subject=["spotlight-%s" % subsite.id])
            
    
    writeDebug('Creating events folder')      

    # Create Events folder
    if 'events' not in subsite.objectIds():
        subsite.invokeFactory(type_name='Folder', id='events', title='Events')
        obj = subsite['events']
        obj.setConstrainTypesMode(1) # restrict what this folder can contain
        obj.setImmediatelyAddableTypes(['Event'])
        obj.setLocallyAllowedTypes(['Event','Topic'])
        obj.reindexObject()

        # Create sample event
        obj.invokeFactory(type_name='Event', id='sample', title='Sample Event', 
                          description='This is a sample Event Item',  start_date='2020-01-01', 
                          end_date='2020-01-01', start_time='13:00', stop_time='14:30', 
                          event_url='http://agsci.psu.edu', location='Anywhere')

        writeDebug('Creating upcoming collection')      
        
        # create a smartfolder for upcoming events inside the events folder, and set it as the default page
        if 'upcoming' not in obj.objectIds():
            obj.invokeFactory(type_name='Topic', id='upcoming', title='Upcoming Events')
            obj.setDefaultPage('upcoming')
            
            smart_obj = obj['upcoming']
            smart_obj.reindexObject()
        
            # Set the criteria for the folder
            type_crit = smart_obj.addCriterion('Type','ATPortalTypeCriterion')
            
            type_crit.setValue(['Event']) # only our specified event types
            
            date_crit = smart_obj.addCriterion('end', 'ATFriendlyDateCriteria')
            date_crit.setValue(0) # Set date reference to now
            date_crit.setDateRange('+') # Only list future events
            date_crit.setOperation('more')
        
        
            path_crit = smart_obj.addCriterion('path','ATPathCriterion')
            path_crit.setValue(obj.UID()) # Only list events in the current subsite
            path_crit.setRecurse(True)
        
            sort_crit = smart_obj.addCriterion('start','ATSortCriterion')

    writeDebug('Setting portlets')
    
    # Set portlets
    # Register some portlets for this subsite's context.
    # Copied mostly from plone.portlets' README doctests.

    subsite_LeftColumn = getPortletAssignmentMapping(subsite, 'plone.leftcolumn')
    subsite_RightColumn = getPortletAssignmentMapping(subsite, 'plone.rightcolumn')
    
    # Block the parent portlets
    writeDebug('Blocking parent portlets')

    writeDebug('Blocking plone.leftcolumn parent portlets')    
    try:
        subsite_LeftColumnManager = getLocalPortletAssignmentManager(subsite, 'plone.leftcolumn')
        subsite_LeftColumnManager.setBlacklistStatus(CONTEXT_CATEGORY, True)
    except ComponentLookupError:
        writeDebug('ERROR blocking plone.leftcolumn parent portlets')    

    writeDebug('Blocking plone.rightcolumn parent portlets')    
    try:
        subsite_RightColumnManager = getLocalPortletAssignmentManager(subsite, 'plone.rightcolumn')
        subsite_RightColumnManager.setBlacklistStatus(CONTEXT_CATEGORY, True)
    except ComponentLookupError:
        writeDebug('ERROR blocking plone.rightcolumn parent portlets')  
        pdb.set_trace() 

    # Set left navigation portlet
    left_navigation = navigation.Assignment(name=u"",
                                            root='/%s' % '/'.join(urltool.getRelativeContentPath(subsite)),
                                            currentFolderOnly = False,
                                            includeTop = True,
                                            topLevel = 0,
                                            bottomLevel = 3)

    subsite_LeftColumn['navigation'] = left_navigation 

    # Create homepage
    if 'default' not in subsite.objectIds():
        subsite_title=str(subsite.title)
        subsite.invokeFactory(type_name='HomePage',id='default',title=subsite_title, text='')
        subsite.setDefaultPage('default')
        default=subsite['default']
        
        # Set portlets for homepage
        homepage_centerColumn = getPortletAssignmentMapping(default, 'agcommon.centercolumn')
        homepage_rightColumn = getPortletAssignmentMapping(default, 'agcommon.rightcolumn')

        # Configure feedmixer in center column

        # Grab path to news RSS feed, and make sure it's http://        
        agsci_rss = 'http://agsci.psu.edu/news/live.psu.edu/agsci/RSS'
        subsite_rss = subsite.absolute_url().replace('https:', 'http:') + '/news/latest/RSS'

        if subsite_rss.count('localhost'):
            feeds=[agsci_rss]
        else:
            feeds=[agsci_rss,subsite_rss]

        subsite_news = feedmixer.portlet.Assignment(
                    title="%s News" % subsite.title,
                    feeds="\n".join(feeds),
                    items_shown=3,
                    show_header=True,
                    show_date=True,
                    show_summary=True,
                    show_image=False,
                    show_footer=False,
                    cache_timeout=1800,
                    assignment_context_path=None)
                    
        saveAssignment(homepage_centerColumn, subsite_news)

        spotlightCollectionPortlet = collection.Assignment(header=u"Spotlight",
                                        target_collection = '/'.join(urltool.getRelativeContentPath(subsite.news.spotlight.recent)),
                                        random=False,
                                        show_more=False,
                                        show_dates=False)

        saveAssignment(homepage_rightColumn, spotlightCollectionPortlet)
                                        
        eventsCollectionPortlet = collection.Assignment(header=u"Upcoming Events",
                                        limit=3,
                                        target_collection = '/'.join(urltool.getRelativeContentPath(subsite.events.upcoming)),
                                        random=False,
                                        show_more=True,
                                        show_dates=True)

        saveAssignment(homepage_rightColumn, eventsCollectionPortlet)
                                        

    writeDebug('Finished creating subsite')     
    #pdb.set_trace() 
    return True

    

    

