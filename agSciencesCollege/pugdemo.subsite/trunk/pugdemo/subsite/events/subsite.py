from Products.CMFCore.utils import getToolByName
from pugdemo.subsite.events import getPortletAssignmentMapping, saveAssignment, writeDebug, getLocalPortletAssignmentManager
from plone.portlet.collection import collection
from plone.app.portlets.portlets import navigation
from plone.portlets.constants import CONTEXT_CATEGORY

# Adds an editors group to the subsite
def addEditorsGroup(subsite):
    group_id = "%s-editors"% str(subsite.id)
    group_title = "%s Editors"% str(subsite.Title())
    
    grouptool = getToolByName(subsite, 'portal_groups')
    
    if grouptool.addGroup(group_id):
        grouptool.getGroupById(group_id).title = group_title
        
    return group_id


# Gives the add/edit/view/review roles on context to a group
def setRoles(context, group):
    context.manage_setLocalRoles(group, ['Contributor', 'Reviewer', 'Editor', 'Reader'])
    context.reindexObjectSecurity()


def onSubsiteCreation(subsite, event):

    # Create editors group and set roles.
    editors_group = addEditorsGroup(subsite)
    setRoles(subsite, editors_group)

    # Get URL tool
    urltool = getToolByName(subsite, 'portal_url')

    # Create 'news' folder
    if 'news' not in subsite.objectIds():
        subsite.invokeFactory(type_name='Folder', id='news', title='News')
        obj = subsite['news']
        obj.setConstrainTypesMode(1) # restrict what this folder can contain
        obj.setImmediatelyAddableTypes(['News Item'])
        obj.setLocallyAllowedTypes(['News Item','Topic'])
        obj.unmarkCreationFlag() 

        # Create sample News Item
        obj.invokeFactory(type_name='News Item', id='sample', title='Sample News Item', 
                          description='This is a sample News Item')

        obj['sample'].unmarkCreationFlag()

        # create a smartfolder for upcoming events inside the events folder, and set it as the default page
        if 'latest' not in obj.objectIds():
            obj.invokeFactory(type_name='Topic', id='latest', title='Latest News')
            obj.setDefaultPage('latest')
            
            smart_obj = obj['latest']
            smart_obj.unmarkCreationFlag()
                    
            # Set the criteria for the folder
            type_crit = smart_obj.addCriterion('Type','ATPortalTypeCriterion')
            
            type_crit.setValue(['News Item']) # only our specified event types
            
            path_crit = smart_obj.addCriterion('path','ATPathCriterion')
            path_crit.setValue(obj.UID()) # Only list events in the current subsite
            path_crit.setRecurse(True)
        
            sort_crit = smart_obj.addCriterion('effective','ATSortCriterion')
 

    # Create Events folder
    if 'events' not in subsite.objectIds():
        subsite.invokeFactory(type_name='Folder', id='events', title='Events')
        obj = subsite['events']
        obj.setConstrainTypesMode(1) # restrict what this folder can contain
        obj.setImmediatelyAddableTypes(['Event'])
        obj.setLocallyAllowedTypes(['Event','Topic'])
        obj.unmarkCreationFlag()

        # Create sample event
        obj.invokeFactory(type_name='Event', id='sample', title='Sample Event', 
                          description='This is a sample Event',  start_date='2020-01-01', 
                          end_date='2020-01-01', start_time='13:00', stop_time='14:30', 
                          event_url='http://agsci.psu.edu', location='Anywhere')

        obj['sample'].unmarkCreationFlag()

        writeDebug('Creating upcoming collection')      
        
        # create a smartfolder for upcoming events inside the events folder, and set it as the default page
        if 'upcoming' not in obj.objectIds():
            obj.invokeFactory(type_name='Topic', id='upcoming', title='Upcoming Events')
            obj.setDefaultPage('upcoming')
            
            smart_obj = obj['upcoming']
            smart_obj.unmarkCreationFlag()
                    
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

    writeDebug('Creating photos folder') 

    # Create homepage
    if 'front-page' not in subsite.objectIds():
        subsite_title=str(subsite.title)
        subsite_description=str(subsite.description)
        subsite.invokeFactory(type_name='Document',id='front-page',title=subsite_title, description=subsite_description, text='<p>Enter some text for your homepage.</p>')
        subsite.setDefaultPage('front-page')
        front_page=subsite['front-page']
        front_page.unmarkCreationFlag()
        
        # Set portlets for homepage
        homepage_rightColumn = getPortletAssignmentMapping(front_page, 'plone.rightcolumn')

        if 'news' in subsite.objectIds() and 'latest' in subsite.news.objectIds():
            newsCollectionPortlet = collection.Assignment(header=u"Latest News",
                                            target_collection = '/'.join(urltool.getRelativeContentPath(subsite.news.latest)),
                                            random=False,
                                            limit=3,
                                            show_more=True,
                                            show_dates=True)
    
            saveAssignment(homepage_rightColumn, newsCollectionPortlet)

        if 'events' in subsite.objectIds() and 'upcoming' in subsite.events.objectIds():
                         
            eventsCollectionPortlet = collection.Assignment(header=u"Upcoming Events",
                                    limit=3,
                                    target_collection = '/'.join(urltool.getRelativeContentPath(subsite.events.upcoming)),
                                    random=False,
                                    show_more=True,
                                    show_dates=True)

            saveAssignment(homepage_rightColumn, eventsCollectionPortlet)

    # Block the parent portlets
    subsite_LeftColumn = getPortletAssignmentMapping(subsite, 'plone.leftcolumn')
    subsite_LeftColumnManager = getLocalPortletAssignmentManager(subsite, 'plone.leftcolumn')
    subsite_LeftColumnManager.setBlacklistStatus(CONTEXT_CATEGORY, True)

    subsite_RightColumn = getPortletAssignmentMapping(subsite, 'plone.rightcolumn')
    subsite_RightColumnManager = getLocalPortletAssignmentManager(subsite, 'plone.rightcolumn')
    subsite_RightColumnManager.setBlacklistStatus(CONTEXT_CATEGORY, True)


    # Set left navigation portlet
    left_navigation = navigation.Assignment(name=u"",
                                            root='/%s' % '/'.join(urltool.getRelativeContentPath(subsite)),
                                            currentFolderOnly = False,
                                            includeTop = True,
                                            topLevel = 0,
                                            bottomLevel = 2)

    subsite_LeftColumn['navigation'] = left_navigation 

                                        

    writeDebug('Finished creating subsite')     
    return True

