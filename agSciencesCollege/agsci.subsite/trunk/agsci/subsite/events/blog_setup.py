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

from agsci.subsite.events.subsite_setup import getPortletAssignmentMapping, getPortletManager, getLocalPortletAssignmentManager, saveAssignment

# Write debug messages to log file
def writeDebug(msg):
    LOG('agsci.subsite', INFO, msg)
    
# What we want to happen when we create a subsite
def onBlogCreation(blog, event):
    writeDebug('Creating blog.')

    writeDebug('Beginning post create script.')

    # Calculate dates
    now = datetime.now()
    current_year = now.year

    # Get URL tool
    urltool = getToolByName(blog, 'portal_url')
    
    writeDebug('Creating news folder')
    
    # Create News folder
    blog.setConstrainTypesMode(1) # restrict what this folder can contain
    blog.setImmediatelyAddableTypes([])
    blog.setLocallyAllowedTypes(['Topic','Folder'])
    blog.reindexObject()
    
    # Create year folders for the past year, and the next 10 years
    archive_years = [str(x) for x in range(current_year-1,current_year+11)]

    for year in archive_years:
        if year not in blog.objectIds():
            writeDebug('Creating archive year folder %s' % year)
            blog.invokeFactory(type_name='Folder', id=year, title=year)
            archive_folder = blog[year]
            archive_folder.setLayout('news_listing')
            archive_folder.setExcludeFromNav(True)
            archive_folder.setConstrainTypesMode(1) # restrict what this folder can contain
            archive_folder.setImmediatelyAddableTypes(['Link','News Item'])
            archive_folder.setLocallyAllowedTypes(['Link','News Item'])
            archive_folder.setEffectiveDate("%s-01-01" % year)
            archive_folder.reindexObject()

    # Create sample news item and set publishing date to 01-01-YYYY
    writeDebug('Creating sample news item')
    current_year_folder = blog[str(current_year)]
    current_year_folder.invokeFactory(type_name='News Item', id='sample', 
                                        title='Sample News Item', description='This is a sample News Item', 
                                        text='<p>You may delete this item</p>')
    sample = current_year_folder['sample']
    sample.setEffectiveDate("%s-01-01" % str(current_year))
    sample.reindexObject()
        
        

    writeDebug('Creating latest news collection')

    # create a smartfolder for latest news items, and set it as the default page
    if 'latest' not in blog.objectIds():
        blog.invokeFactory(type_name='Topic', id='latest', title='Latest News')
        blog.setDefaultPage('latest')
        
        smart_obj = blog['latest']
    
        # Set the criteria for the folder
        type_crit = smart_obj.addCriterion('Type','ATPortalTypeCriterion')
        
        type_crit.setValue(['News Item', 'Link']) # only our specified types
        
        path_crit = smart_obj.addCriterion('path','ATPathCriterion')
        path_crit.setValue(blog.UID()) # Only list news in the news folder
        path_crit.setRecurse(True)

        sort_crit = smart_obj.addCriterion('effective','ATSortCriterion')
        sort_crit.setReversed(True)

    writeDebug('Creating years collection')

    # create a smartfolder for archived news by year inside the folder
    if 'years' not in blog.objectIds():
        blog.invokeFactory(type_name='Topic', id='years', title='Archive')
        
        smart_obj = blog['years']
        smart_obj.setExcludeFromNav(True)
        smart_obj.reindexObject()
    
        # Set the criteria for the folder
        type_crit = smart_obj.addCriterion('Type','ATPortalTypeCriterion')
        
        type_crit.setValue(['Folder']) # only our specified event types
        
        path_crit = smart_obj.addCriterion('path','ATPathCriterion')
        path_crit.setValue(blog.UID()) # Only list events in the news folder
        path_crit.setRecurse(True)

        path_crit = smart_obj.addCriterion('getId','ATListCriterion')
        path_crit.setValue(archive_years)
    
        sort_crit = smart_obj.addCriterion('getId','ATSortCriterion')
        sort_crit.setReversed(True)


    # Add News Archive Portlet to right column
    writeDebug('Adding News Archive Portlet to right column')
    latest_RightColumn = getPortletAssignmentMapping(blog['latest'], 'plone.rightcolumn')
    archiveCollectionPortlet = collection.Assignment(header=u"Archive",
                                    target_collection = '/'.join(urltool.getRelativeContentPath(blog.years)),
                                    random=False,
                                    show_more=False,
                                    show_dates=False)

    saveAssignment(latest_RightColumn, archiveCollectionPortlet)


    writeDebug('Creating events folder')      

    writeDebug('Finished creating blog')     
    #pdb.set_trace() 
    return True

    

    

