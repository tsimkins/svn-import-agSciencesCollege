from Products.CMFCore.utils import getToolByName

from zope.component import getUtility
from zope.component import getMultiAdapter
from zope.app.container.interfaces import INameChooser

from plone.portlets.interfaces import IPortletManager
from plone.portlets.interfaces import IPortletAssignmentMapping, ILocalPortletAssignmentManager
from plone.portlet.collection.collection import Assignment

from plone.portlets.constants import CONTEXT_CATEGORY

from plone.app.portlets.portlets import navigation

from datetime import datetime

# What we want to happen when we create a subsite
def onSubsiteCreation(subsite, event):

    now = datetime.now()
    current_year = now.year

    # Remove top menu
    subsite.manage_addProperty('top-menu', 'none', 'string')
    
    # Create News folder
    if 'news' not in subsite.objectIds():
        subsite.invokeFactory('Folder', id='news', title='News')
        obj = subsite['news']
        obj.setConstrainTypesMode(1) # restrict what this folder can contain
        obj.setImmediatelyAddableTypes([])
        obj.setLocallyAllowedTypes(['Topic','Folder'])
        obj.reindexObject()
        
        # Create year folders for the past year, and the next 10 years
        archive_years = range(current_year-1,current_year+11)

        for year in archive_years:
            year_string = str(year)
            if year_string not in obj.objectIds():
                obj.invokeFactory('Folder', id=year_string, title=year_string)
                archive_folder = obj[year_string]
                archive_folder.setLayout('news_listing')
                archive_folder.setExcludeFromNav(True)
                archive_folder.setConstrainTypesMode(1) # restrict what this folder can contain
                archive_folder.setImmediatelyAddableTypes(['Link','News Item'])
                archive_folder.setLocallyAllowedTypes(['Link','News Item'])
                archive_folder.reindexObject()

        # create a smartfolder for latest news items, and set it as the default page
        if 'latest' not in obj.objectIds():
            obj.invokeFactory('Topic', id='latest', title='Latest News')
            obj.setDefaultPage('latest')
            
            smart_obj = obj['latest']
        
            # Set the criteria for the folder
            type_crit = smart_obj.addCriterion('Type','ATPortalTypeCriterion')
            
            type_crit.setValue(['News Item', 'Link']) # only our specified types
            
            path_crit = smart_obj.addCriterion('path','ATPathCriterion')
            path_crit.setValue(obj.UID()) # Only list news in the news folder
            path_crit.setRecurse(True)

            sort_crit = smart_obj.addCriterion('EffectiveDate','ATSortCriterion')
            sort_crit.setReversed(True)

        # create a smartfolder for archived news by year inside the folder
        if 'years' not in obj.objectIds():
            obj.invokeFactory('Topic', id='years', title='Archive')
            
            smart_obj = obj['years']
        
            # Set the criteria for the folder
            type_crit = smart_obj.addCriterion('Type','ATPortalTypeCriterion')
            
            type_crit.setValue(['Folder']) # only our specified event types
            
            path_crit = smart_obj.addCriterion('path','ATPathCriterion')
            path_crit.setValue(obj.UID()) # Only list events in the news folder
            path_crit.setRecurse(True)

            path_crit = smart_obj.addCriterion('getId','ATListCriterion')
            path_crit.setValue(archive_years)
        
            sort_crit = smart_obj.addCriterion('getId','ATSortCriterion')
            sort_crit.setReversed(True)

        # create a folder for spotlight items inside the news folder
        if 'spotlight' not in obj.objectIds():
            obj.invokeFactory('Folder', id='spotlight', title='Spotlight')
            
            spotlight_obj = obj['spotlight']
            
            spotlight_obj.invokeFactory('Topic', id='recent', title='Spotlight')
            
            smart_obj = spotlight_obj['recent']
        
            # Set the criteria for the folder
            type_crit = smart_obj.addCriterion('Type','ATPortalTypeCriterion')
            
            type_crit.setValue(['Folder']) # only our specified event types
            
            path_crit = smart_obj.addCriterion('path','ATPathCriterion')
            path_crit.setValue(subsite.UID()) # Only list items in the current subsite
            path_crit.setRecurse(True)

            path_crit = smart_obj.addCriterion('getId','ATListCriterion')
            path_crit.setValue(archive_years)
        
            sort_crit = smart_obj.addCriterion('getId','ATSortCriterion')
            sort_crit.setReversed(True)


      

    # Create Events folder
    if 'events' not in subsite.objectIds():
        subsite.invokeFactory('Folder', id='events', title='Events')
        obj = subsite['events']
        obj.setConstrainTypesMode(1) # restrict what this folder can contain
        obj.setImmediatelyAddableTypes(['Event','Topic'])
        obj.setLocallyAllowedTypes(['Event'])
        obj.reindexObject()
        
        # create a smartfolder for upcoming events inside the events folder, and set it as the default page
        if 'upcoming' not in obj.objectIds():
            obj.invokeFactory('Topic', id='upcoming', title='Upcoming Events')
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

    #--------------------------------------------------------------------------------
    # Stuff below is from rwellar
    #--------------------------------------------------------------------------------
    
   
    # create a news folder with a smartfolder as a default page
    if 'news' not in subsite.objectIds():
        subsite.invokeFactory('Folder', id='news', title='News archive')
        obj = subsite['news']
        
        if 'archive' not in obj.objectIds():
            obj.invokeFactory('Topic', id='archive', title='News archive') # create a smartfolder
            obj.setDefaultPage('archive') # set this as the default page for the containing folder
        
            smart_obj = obj['archive']
            smart_obj.setLayout('folder_summary_view')
            smart_obj.reindexObject()
        
            # state_crit = smart_obj.addCriterion('review_state','ATSimpleStringCriterion')
            # state_crit.setValue('published')
        
            type_crit = smart_obj.addCriterion('Type','ATPortalTypeCriterion')
            type_crit.setValue(['News Item'])
        
            path_crit = smart_obj.addCriterion('path','ATPathCriterion')
            path_crit.setValue(subsite.UID()) # Only list news items in the current subsite
            path_crit.setRecurse(True)
        
            sort_crit = smart_obj.addCriterion('effective','ATSortCriterion')
            smart_obj.getSortCriterion().setReversed(True)

        # let only news items be addable inside the news folder
        obj.setConstrainTypesMode(1) 
        obj.setImmediatelyAddableTypes(['News Item','Folder','Topic'])
        obj.setLocallyAllowedTypes(['News Item','Folder','Topic'])
        obj.reindexObject()
    
            
    if 'default' not in subsite.objectIds():
            subsite_title=str(subsite.title)
            subsite.invokeFactory('Document',id='default',title=subsite_title, text='<p>Welcome to the '+subsite_title+'</p>')
            subsite.setDefaultPage('default')
    
    # Register some portlets for this subsite's context.
    # Copied mostly from plone.portlets' README doctests.
    right = getUtility(IPortletManager, name='plone.rightcolumn')
    left = getUtility(IPortletManager, name='plone.leftcolumn')
    rightColumnInThisContext = getMultiAdapter((subsite, right), IPortletAssignmentMapping)
    leftColumnInThisContext = getMultiAdapter((subsite, left), IPortletAssignmentMapping)
    
    urltool  = getToolByName(subsite, 'portal_url')
    # eventsCollectionPortlet = Assignment(header=u"Events",
    #                                             limit=5,
    #                                             target_collection = '/'.join(urltool.getRelativeContentPath(subsite.events.upcoming)),
    #                                             random=False,
    #                                             show_more=True,
    #                                             show_dates=False)
    #         
    newsCollectionPortlet = Assignment(header=u"News",
                                        limit=5,
                                        target_collection = '/'.join(urltool.getRelativeContentPath(subsite.news.archive)),
                                        random=False,
                                        show_more=True,
                                        show_dates=False)
    
    leftColumnInThisContext[u'navigation'] = navigation.Assignment(name=u"",
                                            root='/'.join(urltool.getRelativeContentPath(subsite)),
                                            currentFolderOnly = False,
                                            includeTop = True,
                                            topLevel = 0,
                                            bottomLevel = 2)
    
    def saveAssignment(mapping, assignment):
        chooser = INameChooser(mapping)
        mapping[chooser.chooseName(None, assignment)] = assignment
    
    # saveAssignment(rightColumnInThisContext, eventsCollectionPortlet)
    saveAssignment(rightColumnInThisContext, newsCollectionPortlet)
    
    # Block the parent portlets
    subsiteLeftColumnManager = getMultiAdapter((subsite, left), ILocalPortletAssignmentManager)
    subsiteLeftColumnManager.setBlacklistStatus(CONTEXT_CATEGORY, True)
    subsiteRightColumnManager = getMultiAdapter((subsite, right), ILocalPortletAssignmentManager)
    subsiteRightColumnManager.setBlacklistStatus(CONTEXT_CATEGORY, True) 
