from Products.CMFCore.utils import getToolByName

from zope.component import getUtility
from zope.component import getMultiAdapter
from zope.app.container.interfaces import INameChooser
import pdb

from plone.portlets.interfaces import IPortletManager, IPortletAssignmentMapping, ILocalPortletAssignmentManager

from plone.portlets.constants import CONTEXT_CATEGORY
from collective.contentleadimage.config import IMAGE_FIELD_NAME

from plone.app.portlets.portlets import navigation
from plone.portlet.static import static
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

    # Remove subsite from nav
    subsite.setExcludeFromNav(True)
    subsite.reindexObject()
    
    # Remove top menu
    writeDebug('Removing top menu')
    subsite.manage_addProperty('top-menu', 'none', 'string')

    # Set subsite title
    writeDebug('Setting subsite title')
    subsite.manage_addProperty('site_title', str(subsite.title), 'string')

    writeDebug('Creating news folder')
    
    # Create Blog 'news' folder
    if 'news' not in subsite.objectIds():
        subsite.invokeFactory(type_name='Blog', id='news', title='News')
        # All the other goodies get taken care of through the 'Blog' content type
        # But apparently not automatically.  Let's force it.
        
        news = subsite['news']
        onBlogCreation(news, event)
        news.unmarkCreationFlag() 

        # Let's put a spotlight subfolder, etc. within the news folder from here.
        # Not all blogs need a spotlight folder, and we tie the spotlight tag to the
        # name of the subsite.
    
        writeDebug('Creating spotlight folder')
    
   
        # create a folder for spotlight items inside the news folder
        if 'spotlight' not in news.objectIds():
            news.invokeFactory(type_name='Folder', id='spotlight', title='Spotlight')
            
            spotlight_obj = news['spotlight']
            spotlight_obj.setConstrainTypesMode(1) # restrict what this folder can contain
            spotlight_obj.setImmediatelyAddableTypes(['Link','Folder','File','Document'])
            spotlight_obj.setLocallyAllowedTypes(['Link','Folder','File','Document','Topic'])
            spotlight_obj.unmarkCreationFlag()
            
            writeDebug('Creating recent spotlight topic')
            spotlight_obj.invokeFactory(type_name='Topic', id='recent', title='Spotlight')
            
            smart_obj = spotlight_obj['recent']
            smart_obj.unmarkCreationFlag()
            
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
            
            if 'sample' not in spotlight_obj.objectIds():
                spotlight_obj.invokeFactory(type_name='Document', id='sample',
                                            title='Sample Spotlight Item', description='This is a sample Spotlight Item', 
                                            text='<p>You may delete this item</p>', subject=["spotlight-%s" % subsite.id])
                spotlight_obj['sample'].unmarkCreationFlag()
            
    
    writeDebug('Creating events folder')      

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
                          description='This is a sample Event Item',  start_date='2020-01-01', 
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
    if 'front-page' not in subsite.objectIds():
        subsite_title=str(subsite.title)
        subsite.invokeFactory(type_name='HomePage',id='front-page',title=subsite_title, text='')
        subsite.setDefaultPage('front-page')
        front_page=subsite['front-page']
        front_page.unmarkCreationFlag()
        
        # Set portlets for homepage
        homepage_centerColumn = getPortletAssignmentMapping(front_page, 'agcommon.centercolumn')
        homepage_rightColumn = getPortletAssignmentMapping(front_page, 'agcommon.rightcolumn')

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


# What we want to happen when we create a subsite
def onCountySiteCreation(subsite, event):

    # Get URL tool
    urltool = getToolByName(subsite, 'portal_url')

    # Get county name
    # We ass-u-me that the subsite id is the county name, lowercased.
    county_name = str(subsite.id).title()

    # Set county
    subsite.extension_counties = (county_name,)
    
    # Get the office info for the office
    office_info = {}

    portal_skins = getToolByName(subsite, 'portal_skins')
    
    office_info_file = portal_skins.agsci_subsite['office_info.txt']
    
    lines = office_info_file._readFile(False).replace('\r', '\n').split('\n')
    header = [x.lower() for x in lines.pop(0).split('\t')]
    
    for line in lines:
        fields = line.split('\t')
        
        county = fields[0].lower()
        
        if county == county_name.lower():
            for x in range(0, len(header)):
                office_info[header[x]] = fields[x]

    
    # Programs Folder
    writeDebug('Creating programs folder')
    if not 'programs' in subsite.objectIds():
        subsite.invokeFactory(type_name='Folder', id='programs', title='Programs')
        programs = subsite['programs']
        
        # Make 4-H and Master Gardeners folders
        programs.invokeFactory(type_name='Folder', id='4-h', title='4-H')
        programs['4-h'].unmarkCreationFlag()
        programs['4-h'].setExcludeFromNav(True)
        programs['4-h'].reindexObject()

        programs.invokeFactory(type_name='Folder', id='master-gardeners', title='Master Gardeners')        
        programs['master-gardeners'].unmarkCreationFlag()
        programs['master-gardeners'].setExcludeFromNav(True)
        programs['master-gardeners'].reindexObject()


        programs.unmarkCreationFlag()     
        
        # create a smartfolder for listing the programs in alphabetical order
        if 'listing' not in programs.objectIds():
            programs.invokeFactory(type_name='Topic', id='listing', title='%s Programs' % county_name)
            programs.setDefaultPage('listing')
            
            smart_obj = programs['listing']
            smart_obj.unmarkCreationFlag()
                    
            # Set the criteria for the folder
            type_crit = smart_obj.addCriterion('Type','ATPortalTypeCriterion')
            
            type_crit.setValue(['Folder', 'Link', 'Subsite', 'Section']) # only our specified event types
        
            path_crit = smart_obj.addCriterion('path','ATPathCriterion')
            path_crit.setValue(programs.UID()) # Only list events in the current subsite
            path_crit.setRecurse(False)
        
            sort_crit = smart_obj.addCriterion('sortable_title','ATSortCriterion')   
        
    # Add all the subsite goodies
    writeDebug('Running subsite populations script')
    onSubsiteCreation(subsite, event)
    
    # Directory 
    writeDebug('Adding directory collection')
    if not 'directory' in subsite.objectIds():
        subsite.invokeFactory(type_name='Topic', id='directory', title='Directory')
        smart_obj = subsite['directory']
        
        smart_obj.setLayout('folder_summary_view')
        
        # Set the criteria for the folder
        county_crit = smart_obj.addCriterion('Counties','ATSelectionCriterion')
        county_crit.setValue(county_name) # Only list items in the current subsite

        type_crit = smart_obj.addCriterion('Type','ATPortalTypeCriterion')
        type_crit.setValue(['Person']) # only our specified types
                
        sort_crit = smart_obj.addCriterion('sortable_title','ATSortCriterion')
        sort_crit.setReversed(True)

        smart_obj.unmarkCreationFlag()


    # Directions 
    writeDebug('Adding directions page')
    if not 'directions' in subsite.objectIds():
        subsite.invokeFactory(type_name='Document', id='directions', 
        title='Directions to %s Extension Office' % county_name,
        text="""
<h2>Driving Directions</h2>
<iframe src="http://maps.google.com/maps?q=%(address_1)s+%(city)s+%(state)s&amp;output=embed" 
        frameborder="0" marginwidth="0" marginheight="0" scrolling="no" height="480" width="100%%"></iframe>
<p class="discreet"><a style="text-align: left;" href="http://maps.google.com/maps?q=%(address_1)s+%(city)s+%(state)s">View Larger Map</a></p>

        """ % {
            'address_1' : office_info.get('address_1'),
            'city' : office_info.get('city'),
            'state' : office_info.get('state'),
        })
        directions = subsite['directions']
        directions.setExcludeFromNav(True)
        directions.reindexObject()
        directions.unmarkCreationFlag()
        
    # Assign portlets
    writeDebug('Creating portlets')
    subsite_LeftColumn = getPortletAssignmentMapping(subsite, 'plone.leftcolumn')
    subsite_RightColumn = getPortletAssignmentMapping(subsite, 'plone.rightcolumn')
        
    # Create Office Info portlet
    writeDebug('Creating Office Info portlet')
    office_text = """
    <h2>Address</h2>
    <p>%(address_1)s<br />
    %(address_2)s
    %(city)s, %(state)s %(zip)s</p>
    <h2>Contact</h2>
    <p>Phone: %(phone)s<br />
    Fax: %(fax)s<br />
    Email: <a href="mailto:%(email)s">%(email)s</a></p>
    <h2>Office Hours</h2>
    <p>%(office_hours)s</p>
    <h2>Directions</h2>
    <p><a href="/%(county)s/directions">Directions to our office</a></p>
    """ % {
        'county' : county_name.lower(),
        'address_1' : office_info.get('address_1'),
        'address_2' : office_info.get('address_2') and office_info.get('address_2') + '<br />' or '',
        'city' : office_info.get('city'),
        'state' : office_info.get('state'),
        'zip' : office_info.get('zip'),
        'phone' : office_info.get('phone'),
        'fax' : office_info.get('fax'),
        'email' : office_info.get('email'),
        'office_hours' : office_info.get('office_hours'),
    }
    
    
    office_info_portlet = static.Assignment(header="Office Information",
                                            text=office_text)

    subsite_LeftColumn['office-information'] = office_info_portlet 
    
    
    # Configure homepage
    if 'front-page' in subsite.objectIds():
        writeDebug("Configuring homepage")
        front_page = subsite['front-page']
        front_page.setLayout('document_subsite_view')

        writeDebug("Configuring homepage portlets")
        homepage_rightColumn = getPortletAssignmentMapping(front_page, 'plone.rightcolumn')

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

        # Set homepage image
        writeDebug("Setting homepage image")
        portal_skins = getToolByName(subsite, 'portal_skins')
        subsite_homepage_image = portal_skins.agsci_subsite['subsite_homepage_placeholder.jpg']._readFile(False)
        front_page.getField(IMAGE_FIELD_NAME).set(front_page, subsite_homepage_image)

    # Update Events criteria:  Remove location (path) and add Counties
    if 'events' in subsite.objectIds() and 'upcoming' in subsite.events.objectIds():
        writeDebug("Updating events collection")

        upcoming = subsite.events.upcoming

        #Deleting path criteria
        upcoming.deleteCriterion('crit__path_ATPathCriterion')
        
        #Adding county criteria
        county_crit = upcoming.addCriterion('Counties','ATSelectionCriterion')
        county_crit.setValue(county_name) # Only list items in the current subsite


    # Update News criteria:  Remove location (path) and  and add Counties
    if 'news' in subsite.objectIds() and 'latest' in subsite.news.objectIds():
        writeDebug("Updating news collection")
        latest = subsite.news.latest

        #Deleting path criteria
        latest.deleteCriterion('crit__path_ATPathCriterion')
        
        #Adding county criteria
        county_crit = latest.addCriterion('Counties','ATSelectionCriterion')
        county_crit.setValue(county_name) # Only list items in the current subsite     

    #pdb.set_trace() 

    return True

    
# What we want to happen when we create a blog
def onBlogCreation(blog, event):
    writeDebug('Creating blog.')

    writeDebug('Beginning post create script.')

    # Calculate dates
    now = datetime.now()
    current_year = now.year

    # Get URL tool
    urltool = getToolByName(blog, 'portal_url')
    
    writeDebug('Setting addable types')
    
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
            archive_folder.unmarkCreationFlag()
            archive_folder.reindexObject()
            
    # Create sample news item and set publishing date to 01-01-YYYY
    writeDebug('Creating sample news item')
    current_year_folder = blog[str(current_year)]
    current_year_folder.invokeFactory(type_name='News Item', id='sample', 
                                        title='Sample News Item', description='This is a sample News Item', 
                                        text='<p>You may delete this item</p>')
    sample = current_year_folder['sample']
    sample.setEffectiveDate("%s-01-01" % str(current_year))
    sample.unmarkCreationFlag()        
        

    writeDebug('Creating latest news collection')

    # create a smartfolder for latest news items, and set it as the default page
    if 'latest' not in blog.objectIds():
        blog.invokeFactory(type_name='Topic', id='latest', title='Latest News')
        blog.setDefaultPage('latest')
        
        smart_obj = blog['latest']
        smart_obj.unmarkCreationFlag()
    
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
        smart_obj.unmarkCreationFlag()
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

    writeDebug('Finished creating blog')     
    #pdb.set_trace() 
    return True
    
# What we want to happen when we create a section
def onSectionCreation(section, event):

    writeDebug('Beginning post create script.')

    # Remove from left nav
    section.setLayout('folder_listing')
    section.setExcludeFromNav(True)
    section.reindexObject()
    
    # Get URL tool
    urltool = getToolByName(section, 'portal_url')
    
    # Set portlets
    # Register some portlets for this section's context.
    # Copied mostly from plone.portlets' README doctests.

    section_LeftColumn = getPortletAssignmentMapping(section, 'plone.leftcolumn')
    section_RightColumn = getPortletAssignmentMapping(section, 'plone.rightcolumn')
    
    # Block the parent portlets
    writeDebug('Blocking parent portlets')

    writeDebug('Blocking plone.leftcolumn parent portlets')    
    try:
        section_LeftColumnManager = getLocalPortletAssignmentManager(section, 'plone.leftcolumn')
        section_LeftColumnManager.setBlacklistStatus(CONTEXT_CATEGORY, True)
    except ComponentLookupError:
        writeDebug('ERROR blocking plone.leftcolumn parent portlets')    

    writeDebug('Blocking plone.rightcolumn parent portlets')    
    try:
        section_RightColumnManager = getLocalPortletAssignmentManager(section, 'plone.rightcolumn')
        section_RightColumnManager.setBlacklistStatus(CONTEXT_CATEGORY, True)
    except ComponentLookupError:
        writeDebug('ERROR blocking plone.rightcolumn parent portlets')  
        pdb.set_trace() 

    # Set left navigation portlet
    left_navigation = navigation.Assignment(name=u"",
                                            root='/%s' % '/'.join(urltool.getRelativeContentPath(section)),
                                            currentFolderOnly = False,
                                            includeTop = True,
                                            topLevel = 0,
                                            bottomLevel = 3)

    section_LeftColumn['navigation'] = left_navigation 
    
    #Adding sample page
    
    if 'sample' not in section.getObjectIds():
        section.invokeFactory(type_name='Document', id='sample', title='Sample Page', description='This is a sample Page', text='<p>You may delete this item</p>')
        section['sample'].unmarkCreationFlag()
    
    writeDebug('Finished creating section')     
    #pdb.set_trace() 
    return True

