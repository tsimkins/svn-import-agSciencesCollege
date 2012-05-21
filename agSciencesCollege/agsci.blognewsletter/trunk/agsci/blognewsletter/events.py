from Products.CMFCore.utils import getToolByName

from zope.component import getUtility
from zope.component import getMultiAdapter
from zope.app.container.interfaces import INameChooser

from agsci.blognewsletter.portlet import tags

from plone.portlets.interfaces import IPortletManager, IPortletAssignmentMapping, ILocalPortletAssignmentManager

from plone.portlet.collection import collection

from datetime import datetime

from zLOG import LOG, INFO

from zope.component.interfaces import ComponentLookupError

from plone.portlets.constants import CONTEXT_CATEGORY

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
    LOG('agsci.blognewsletter', INFO, msg)

# What we want to happen when we create a blog
def onBlogCreation(blog, event):
    writeDebug('Creating blog.')

    writeDebug('Beginning post create script.')

    # Calculate dates
    now = datetime.now()
    current_timestamp = now.strftime('%Y-%m-%d %H:%M')
    current_year = now.year

    # Get URL tool
    urltool = getToolByName(blog, 'portal_url')
    
    writeDebug('Setting addable types')
    
    # Create News folder
    blog.setConstrainTypesMode(1) # restrict what this folder can contain
    blog.setImmediatelyAddableTypes(['Newsletter'])
    blog.setLocallyAllowedTypes(['Topic','Folder','Newsletter'])
    blog.reindexObject()
    
    # Create year folders for the past year, and the next 10 years
    archive_years = [str(x) for x in range(current_year-1,current_year+11)]

    for year in archive_years:
        if year not in blog.objectIds():
            writeDebug('Creating archive year folder %s' % year)
            blog.invokeFactory(type_name='Folder', id=year, title=year)
            archive_folder = blog[year]
            archive_folder.setLayout('folder_listing')
            archive_folder.setExcludeFromNav(True)
            archive_folder.setConstrainTypesMode(1) # restrict what this folder can contain
            archive_folder.setImmediatelyAddableTypes(['News Item',])
            archive_folder.setLocallyAllowedTypes(['News Item'])
            archive_folder.setEffectiveDate("%s-01-01" % year)
            archive_folder.unmarkCreationFlag()
            archive_folder.reindexObject()
            
    # Create sample news item and set publishing date to 01-01-YYYY
    writeDebug('Creating sample news item')
    current_year_folder = blog[str(current_year)]
    current_year_folder.invokeFactory(type_name='News Item', id='sample', 
                                        title='Sample News Item', description='This is a sample News Item', 
                                        text='<p>You may delete this item</p>')
    sample = current_year_folder['sample']
    sample.setEffectiveDate(current_timestamp)
    sample.unmarkCreationFlag()        
        

    writeDebug('Creating latest news collection')

    # Creating latest news collection
    
    for (id, title) in [['latest', 'Latest News']]:

        if id not in blog.objectIds():
            blog.invokeFactory(type_name='Topic', id=id, title=title)

            smart_obj = blog[id]
            smart_obj.setLayout('folder_summary_view')
            smart_obj.setExcludeFromNav(True)
            smart_obj.unmarkCreationFlag()
            smart_obj.reindexObject()

            # Set the criteria for the folder
            type_crit = smart_obj.addCriterion('Type','ATPortalTypeCriterion')
            
            type_crit.setValue(['News Item']) # only our specified types
            
            path_crit = smart_obj.addCriterion('path','ATPathCriterion')
            search_folders = [blog[x].UID() for x in archive_years]
            path_crit.setValue(search_folders) # Only list news in the news year folders
            path_crit.setRecurse(True)

            sort_crit = smart_obj.addCriterion('effective','ATSortCriterion')
            sort_crit.setReversed(True)
    
    # Set default page to the latest news collection
    writeDebug('Setting default page of blog')
    blog.setDefaultPage('latest')

    writeDebug('Creating years collection')

    # create a smartfolder for archived news by year inside the folder
    if 'years' not in blog.objectIds():
        blog.invokeFactory(type_name='Topic', id='years', title='Archive')
        
        smart_obj = blog['years']
        smart_obj.setExcludeFromNav(True)
        smart_obj.unmarkCreationFlag()
        smart_obj.reindexObject()
    
        # Set the criteria for the folder
        type_crit = smart_obj.addCriterion('Type','ATPortalTypeCriterion')
        
        type_crit.setValue(['Folder']) # only our specified event types
        
        path_crit = smart_obj.addCriterion('path','ATPathCriterion')
        path_crit.setValue(blog.UID()) # Only list events in the news folder
        path_crit.setRecurse(True)

        id_crit = smart_obj.addCriterion('getId','ATListCriterion')
        id_crit.setValue(archive_years)

        effective_crit = smart_obj.addCriterion('effective', 'ATFriendlyDateCriteria')
        effective_crit.setOperation('less') # Less than
        effective_crit.setValue(0) # "Now"
        effective_crit.setDateRange('-') # in the past

        sort_crit = smart_obj.addCriterion('getId','ATSortCriterion')
        sort_crit.setReversed(True)


    # Block parent portlets on right column of blog
    writeDebug('Blocking plone.rightcolumn parent portlets for Blog')    
    try:
        subsite_RightColumnManager = getLocalPortletAssignmentManager(blog, 'plone.rightcolumn')
        subsite_RightColumnManager.setBlacklistStatus(CONTEXT_CATEGORY, True)
    except ComponentLookupError:
        writeDebug('ERROR blocking plone.rightcolumn parent portlets for Blog')  

    # Block parent portlets on right column of blog default collection
    writeDebug('Blocking plone.rightcolumn parent portlets for Latest News')    
    try:
        subsite_RightColumnManager = getLocalPortletAssignmentManager(blog.latest, 'plone.rightcolumn')
        subsite_RightColumnManager.setBlacklistStatus(CONTEXT_CATEGORY, True)
    except ComponentLookupError:
        writeDebug('ERROR blocking plone.rightcolumn parent portlets for Latest News')  

    # Add Latest News Portlet to right column
    writeDebug('Adding Latest News Portlet to right column')
    blog_RightColumn = getPortletAssignmentMapping(blog, 'plone.rightcolumn')
    latestCollectionPortlet = collection.Assignment(header=u"Latest News",
                                    target_collection = '/'.join(urltool.getRelativeContentPath(blog.latest)),
                                    limit=5,
                                    random=False,
                                    show_more=False,
                                    show_dates=True)

    saveAssignment(blog_RightColumn, latestCollectionPortlet)

    # Add Tags Portlet to right column
    writeDebug('Adding Tags Portlet to right column')
    tagsPortlet = tags.Assignment(header=u"Tags",
                                    show_header=True)

    saveAssignment(blog_RightColumn, tagsPortlet)


    # Add News Archive Portlet to right column
    writeDebug('Adding News Archive Portlet to right column')
    latest_RightColumn = getPortletAssignmentMapping(blog['latest'], 'plone.rightcolumn')
    archiveCollectionPortlet = collection.Assignment(header=u"Archive",
                                    target_collection = '/'.join(urltool.getRelativeContentPath(blog.years)),
                                    limit=5,
                                    random=False,
                                    show_more=False,
                                    show_dates=False)

    saveAssignment(latest_RightColumn, archiveCollectionPortlet)

    # Add Tags Portlet to right column
    writeDebug('Adding Tags Portlet to right column')
    latest_RightColumn = getPortletAssignmentMapping(blog['latest'], 'plone.rightcolumn')
    tagsPortlet = tags.Assignment(header=u"Tags",
                                    show_header=True)

    saveAssignment(latest_RightColumn, tagsPortlet)

    writeDebug('Finished creating blog')    
    
    return True

# What we want to happen when we create a subsite
def onNewsletterCreation(newsletter, event):

    # Rename to id 'newsletter' if not already taken
    parent = newsletter.getParentNode()
    if newsletter.id != 'newsletter' and 'newsletter' not in parent.objectIds():
        parent.manage_renameObject(newsletter.id, 'newsletter')
               
    theCriteria = newsletter.addCriterion('effective', 'ATFriendlyDateCriteria')
    theCriteria.setOperation('less') # Less than
    theCriteria.setValue(31) # One Month
    theCriteria.setDateRange('-') # in the past

    sort_crit = newsletter.addCriterion('effective','ATSortCriterion')
    sort_crit.setReversed(True)

    newsletter.itemCount = 99999
    newsletter.unmarkCreationFlag()

    # Block parent portlets on right column of blog
    writeDebug('Blocking plone.rightcolumn parent portlets')    
    try:
        subsite_RightColumnManager = getLocalPortletAssignmentManager(newsletter, 'plone.rightcolumn')
        subsite_RightColumnManager.setBlacklistStatus(CONTEXT_CATEGORY, True)
    except ComponentLookupError:
        writeDebug('ERROR blocking plone.rightcolumn parent portlets')  

    return True
