from Products.CMFCore.utils import getToolByName

from zope.component import getUtility
from zope.component import getMultiAdapter
from zope.app.container.interfaces import INameChooser
import pdb

from plone.portlets.interfaces import IPortletManager, IPortletAssignmentMapping, ILocalPortletAssignmentManager

from plone.portlets.constants import CONTEXT_CATEGORY
from collective.contentleadimage.config import IMAGE_FIELD_NAME

from plone.app.portlets.portlets import navigation
from collective.portlet import feedmixer
from plone.portlet.collection import collection
from Products.agCommon.portlet import linkbutton, linkicon, contact, person

from constants import getCountyWeather, topic_folders

from datetime import datetime

from zLOG import LOG, INFO

from random import random, seed

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
        
 
# What we want to happen when we create a subsite
def onSubsiteCreation(subsite, event, add_group=True, is_plone_site=False, is_county_site=False):

    writeDebug('Beginning post create script.')

    # Get URL tool
    urltool = getToolByName(subsite, 'portal_url')

    # Get portal_skins
    portal_skins = getToolByName(subsite, 'portal_skins')

    # Add group for subsite and set permissions
    if add_group:
        editors_group = addEditorsGroup(subsite)
        setRoles(subsite, editors_group)

    # We're cheating and reusing this code to lay out root Plone sites.
    # Some things don't apply, so we set the default of 'is_plone_site' to
    # False, and override with True when we're running this on a Plone site.
    
    if not is_plone_site:
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
    
    # Create 'background-images' folder
    if 'background-images' not in subsite.objectIds():
        subsite.invokeFactory(type_name='Folder', id='background-images', title='Background Images')
        background_images = subsite['background-images']
        background_images.setExcludeFromNav(True)
        background_images.reindexObject()
        background_images.unmarkCreationFlag()

        background_images.invokeFactory(type_name='Image', id='homepage_placeholder.jpg',
                                        title='Homepage Placeholder', 
                                        image=portal_skins.agcommon_images['homepage_placeholder.jpg']._readFile(False))
        homepage_placeholder = background_images['homepage_placeholder.jpg']
        homepage_placeholder.unmarkCreationFlag()
    
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
            spotlight_obj.setLocallyAllowedTypes(['Link','Folder','File','Document','Topic','Photo Folder'])
            spotlight_obj.unmarkCreationFlag()
            
            writeDebug('Creating recent spotlight topic')
            spotlight_obj.invokeFactory(type_name='Topic', id='recent', title='Spotlight')
            
            smart_obj = spotlight_obj['recent']
            smart_obj.unmarkCreationFlag()
            
            spotlight_obj.setDefaultPage('recent')
        
            if not is_plone_site:
                # Set the criteria for the folder
                path_crit = smart_obj.addCriterion('path','ATPathCriterion')
                path_crit.setValue(subsite.UID()) # Only list items in the current subsite
                path_crit.setRecurse(True)
                spotlight_tag = "spotlight-%s" % subsite.id
            else:
                spotlight_tag = "spotlight"
    
            # Set the criteria for the folder
            tag_crit = smart_obj.addCriterion('Subject','ATSelectionCriterion')
            tag_crit.setValue(spotlight_tag) 
        
            sort_crit = smart_obj.addCriterion('sortable_title','ATSortCriterion')
            
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
        
        # Create a 'files' folder if we're a county subsite.
        # Normally this would go in the onCountySiteCreation method, but
        # then we would have to mess with the addable types, and then set
        # them back to what they should be.
        
        if is_county_site:
            obj.invokeFactory(type_name='Folder', id='files', title='Files')
            files = obj['files']
            files.setConstrainTypesMode(1) # restrict what this folder can contain
            files.setImmediatelyAddableTypes(['File'])
            files.setLocallyAllowedTypes(['File','Folder'])
            files.setExcludeFromNav(True)
            files.reindexObject()
            files.unmarkCreationFlag()
        
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

    writeDebug('Creating photos folder') 

    # Create 'Photos' collection (off by default)
    if 'photos' not in subsite.objectIds():
        
        subsite.invokeFactory(type_name='Folder', id='photos', title='Photos')
        
        photos = subsite['photos']
        photos.setExcludeFromNav(True)
        photos.unmarkCreationFlag()
        photos.reindexObject()
            
        if 'listing' not in photos.objectIds():

            photos.invokeFactory(type_name='Topic', id='listing', title='Photos')
            photos.setDefaultPage('listing')

            listing = photos['listing']
            listing.setLayout('news_listing')
            listing.unmarkCreationFlag()
                   
            # Set the criteria for the folder
            type_crit = listing.addCriterion('Type','ATPortalTypeCriterion')
            
            type_crit.setValue(['Photo Folder']) # only our specified types
            
            if not is_plone_site:
                path_crit = listing.addCriterion('path','ATPathCriterion')
                path_crit.setValue(subsite.UID()) 
                path_crit.setRecurse(True)
    
            sort_crit = listing.addCriterion('effective','ATSortCriterion')
            sort_crit.setReversed(True)
            

    writeDebug('Setting portlets')
    
    if not is_plone_site:
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
            #pdb.set_trace() 
    
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
        county_rss = subsite.absolute_url().replace('https:', 'http:') + '/news/recent/RSS'
        
        if is_county_site:
            feeds=[county_rss]
        elif subsite_rss.count('localhost'):
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

        if 'news' in subsite.objectIds() and 'spotlight' in subsite.news.objectIds() and 'recent' in subsite.news.spotlight.objectIds():
            spotlightCollectionPortlet = collection.Assignment(header=u"Spotlight",
                                            target_collection = '/'.join(urltool.getRelativeContentPath(subsite.news.spotlight.recent)),
                                            random=False,
                                            show_more=False,
                                            show_dates=False)
    
            saveAssignment(homepage_rightColumn, spotlightCollectionPortlet)

        if 'events' in subsite.objectIds() and 'upcoming' in subsite.events.objectIds():
                         
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

    # Add an editors group for the subsite
    editors_group = addEditorsGroup(subsite)
    
    # Get URL tool
    urltool = getToolByName(subsite, 'portal_url')

    # Get county name
    # We ass-u-me that the subsite id is the county name, lowercased.
    county_name = str(subsite.id).title()
    county_id = str(subsite.id).lower()

    # Get the office info for the office
    office_info = {}

    portal_skins = getToolByName(subsite, 'portal_skins')
    
    office_info_file = portal_skins.agsci_subsite['office_info.txt']
    
    lines = office_info_file._readFile(False).replace('\r', '\n').split('\n')
    header = [x.lower() for x in lines.pop(0).split('\t')]
    
    for line in lines:
        fields = line.split('\t')
        
        county = fields[0].lower().strip()
        
        if county == county_id:
            for x in range(0, len(header)):
                office_info[header[x]] = fields[x]

    # Add groups for site

    # Programs Folder
    writeDebug('Creating programs folder')
    if not 'programs' in subsite.objectIds():
        subsite.invokeFactory(type_name='Folder', id='programs', title='Programs')
        programs = subsite['programs']
        programs.unmarkCreationFlag()     

        setRoles(programs, editors_group)
        
        # Set restrictions 
        programs.setConstrainTypesMode(1) # restrict what this folder can contain
        programs.setImmediatelyAddableTypes(['Link','Folder','File','Document'])
        programs.setLocallyAllowedTypes(['Link','Folder','File','Document','Topic','Photo Folder'])
            
        # Make 4-H and Master Gardener folders
        createProgram(subsite=subsite, programs=programs, program_id='4-h', program_name='4-H', 
                      county_name=county_name)

        createProgram(subsite=subsite, programs=programs, program_id='master-gardener', program_name='Master Gardener', 
                      county_name=county_name)
        
        # create a smartfolder for listing the programs in alphabetical order
        if 'listing' not in programs.objectIds():
            programs.invokeFactory(type_name='Topic', id='listing', title='%s County Programs' % county_name, itemCount=99999)
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

    # Set county for subsite
    subsite.extension_counties = (county_name,)

    # Add all the subsite goodies.  Don't add the group and set the permissions.  
    # We're locking the county editing roles down to just News, Events, etc.
    writeDebug('Running subsite populations script')
    onSubsiteCreation(subsite, event, add_group=False, is_county_site=True)

    # Directory 
    writeDebug('Adding directory collection')
    if not 'directory' in subsite.objectIds():
        subsite.invokeFactory(type_name='Topic', id='directory', title='Directory', itemCount=99999)
        smart_obj = subsite['directory']
        
        smart_obj.setLayout('folder_summary_view')
        
        # Set the criteria for the folder
        county_crit = smart_obj.addCriterion('Counties','ATSelectionCriterion')
        county_crit.setValue(county_name) # Only list items in the current subsite

        type_crit = smart_obj.addCriterion('Type','ATPortalTypeCriterion')
        type_crit.setValue(['Person']) # only our specified types
                
        sort_crit = smart_obj.addCriterion('getSortableName','ATSortCriterion')

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

        # Hide all portlets from directions  
        directions_LeftColumnManager = getLocalPortletAssignmentManager(directions, 'plone.leftcolumn')
        directions_LeftColumnManager.setBlacklistStatus(CONTEXT_CATEGORY, True)  

    # Assign portlets
    writeDebug('Creating portlets')
    subsite_LeftColumn = getPortletAssignmentMapping(subsite, 'plone.leftcolumn')
    subsite_RightColumn = getPortletAssignmentMapping(subsite, 'plone.rightcolumn')
        
    # Create Office Info portlet
    
    office_address_lines = [office_info.get('address_1')]
    
    if office_info.get('address_2'):
        office_address_lines.append(office_info.get('address_2'))
        
    office_address_lines.append("%s, %s %s" % (office_info.get('city'), office_info.get('state'), office_info.get('zip')))

    office_address = "\n".join(office_address_lines)
    
    office_info_portlet = contact.Assignment(header=u"Office Information", show_header=True, 
                                             address=office_address,
                                             directions_text="Directions to our office", directions_link="/%s/directions" % county_id, 
                                             office_hours=office_info.get('office_hours'), phone=office_info.get('phone'), 
                                             fax=office_info.get('fax'), email=office_info.get('email'))
    
    link_button = linkbutton.Assignment(items="%s_buttons" % county_id, show_header=False)
    link_icons = linkicon.Assignment(items="%s_links" % county_id, show_header=False)
        
    subsite_LeftColumn['office-information'] = office_info_portlet 
    subsite_LeftColumn['buttons'] = link_button 
    subsite_LeftColumn['icons'] = link_icons
        
    # Configure homepage
    if 'front-page' in subsite.objectIds():
        writeDebug("Configuring homepage")
        front_page = subsite['front-page']
        front_page.setLayout('document_subsite_view')

        writeDebug("Configuring homepage portlets")

        homepage_rightColumn = getPortletAssignmentMapping(front_page, 'plone.rightcolumn')
        homepage_centerColumn = getPortletAssignmentMapping(front_page, 'agcommon.centercolumn')
        
        
        # Configure feedmixer in center column

        feeds=['http://agsci.psu.edu/news/live.psu.edu/extension/RSS']

        subsite_news = feedmixer.portlet.Assignment(
                    title="Penn State Cooperative Extension News",
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
        

        currentIssuesCollectionPortlet = collection.Assignment(header=u"State-Wide Resources",
                                        target_collection = '/state-wide-resources',
                                        random=False,
                                        show_more=False,
                                        show_dates=False)

        saveAssignment(homepage_rightColumn, currentIssuesCollectionPortlet)
        


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
        # Pick from existing Extension images
        writeDebug("Setting homepage image")
        portal_skins = getToolByName(subsite, 'portal_skins')
        background_images = portal_skins.agsci_subsite['background-images']

        image_listing = background_images.objectIds('Filesystem Image')
        image_index = int(random()*len(image_listing))
                
        random_image = background_images[image_listing[image_index]]
        front_page.getField(IMAGE_FIELD_NAME).set(front_page, random_image._readFile(False))

    # Update Events criteria:  Remove location (path) and add Counties
    if 'events' in subsite.objectIds() and 'upcoming' in subsite.events.objectIds():
        writeDebug("Updating events collection")

        setRoles(subsite.events, editors_group)

        upcoming = subsite.events.upcoming

        #Deleting path criteria
        upcoming.deleteCriterion('crit__path_ATPathCriterion')
        
        #Adding county criteria
        county_crit = upcoming.addCriterion('Counties','ATSelectionCriterion')
        county_crit.setValue(county_name) # Only list items in the current subsite


    # Update News criteria
    if 'news' in subsite.objectIds() and 'latest' in subsite.news.objectIds():

        news = subsite['news']

        writeDebug("Updating news collection")

        setRoles(subsite.news, editors_group)


        
        # Make Spotlight only show items in Spotlight folder.
        if 'spotlight' in news.objectIds() and 'recent' in news['spotlight'].objectIds():

            spotlight = news['spotlight']
            smart_obj = news['spotlight']['recent']

            smart_obj.deleteCriterion('crit__path_ATPathCriterion')
            smart_obj.deleteCriterion('crit__Subject_ATSelectionCriterion')

            path_crit = smart_obj.addCriterion('path','ATPathCriterion')
            path_crit.setValue(spotlight.UID()) # Only list items in the current subsite
            path_crit.setRecurse(False)

            type_crit = smart_obj.addCriterion('Type','ATPortalTypeCriterion')
            
            type_crit.setValue(['File', 'Page', 'Link', 'Folder', 'Photo Folder']) # only our specified types

        # Remove 'spotlight-county' tag from sample spotlight item.

        if 'spotlight' in news.objectIds() and 'sample' in news['spotlight'].objectIds():

            spotlight = news['spotlight']

            found_weather = False

            for (title, url) in getCountyWeather(county_name):
                found_weather = True
                id = title.lower().replace(' ', '-')
                spotlight.invokeFactory(type_name='Link', id=id, title=title, remote_url=url)
                link_obj = spotlight[id]
                link_obj.unmarkCreationFlag()
                link_obj.setExcludeFromNav(True)
                link_obj.reindexObject()
                

            if found_weather:
                spotlight.manage_delObjects(['sample'])
            else:
                sample = spotlight['sample']
                sample.setSubject([])
                sample.reindexObject()

    # Unset county for subsite. 
    subsite.extension_counties = ()
    
    return True

    
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
            archive_folder.setImmediatelyAddableTypes(['Link','News Item',])
            archive_folder.setLocallyAllowedTypes(['Link','News Item','Photo Folder'])
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

    # create 'recent' and 'latest' collections
    
    for (id, title) in [['latest', 'Latest News'], ['recent', 'Recent News']]:
    
        if id not in blog.objectIds():
            blog.invokeFactory(type_name='Topic', id=id, title=title)
            
            smart_obj = blog[id]
            smart_obj.setLayout('folder_leadimage_view')
            smart_obj.manage_addProperty('show_date', True, 'boolean')
            smart_obj.setExcludeFromNav(True)
            smart_obj.unmarkCreationFlag()
            smart_obj.reindexObject()
                    
            # Set the criteria for the folder
            type_crit = smart_obj.addCriterion('Type','ATPortalTypeCriterion')
            
            type_crit.setValue(['News Item', 'Link', 'Photo Folder']) # only our specified types
            
            path_crit = smart_obj.addCriterion('path','ATPathCriterion')
            search_folders = [blog[x].UID() for x in archive_years]
            path_crit.setValue(search_folders) # Only list news in the news year folders
            path_crit.setRecurse(True)
    
            sort_crit = smart_obj.addCriterion('effective','ATSortCriterion')
            sort_crit.setReversed(True)
    
    # Set default page to the latest news collection
    blog.setDefaultPage('latest')


    # Add criteria of 'published in last three months' if collection is recent
    recent = blog['recent']
    theCriteria = recent.addCriterion('effective', 'ATFriendlyDateCriteria')
    theCriteria.setOperation('less') # Less than
    theCriteria.setValue(93) # Three Months
    theCriteria.setDateRange('-') # in the past
            
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
        #pdb.set_trace() 

    # Set left navigation portlet
    left_navigation = navigation.Assignment(name=u"",
                                            root='/%s' % '/'.join(urltool.getRelativeContentPath(section)),
                                            currentFolderOnly = False,
                                            includeTop = True,
                                            topLevel = 0,
                                            bottomLevel = 3)

    section_LeftColumn['navigation'] = left_navigation 
    
    # Add restrictions to section 
    section.setConstrainTypesMode(1) # restrict what this folder can contain
    section.setImmediatelyAddableTypes(['Link','Folder','File','Document'])
    section.setLocallyAllowedTypes(['Link','Folder','File','Document','Topic','Subsite','Photo Folder'])
           
    #Adding sample page
    
    if 'sample' not in section.objectIds():
        section.invokeFactory(type_name='Document', id='sample', title='Sample Page', description='This is a sample Page', text='<p>You may delete this item</p>')
        section['sample'].unmarkCreationFlag()
    
    writeDebug('Finished creating section')     
    #pdb.set_trace() 
    
    return True

# What we want to happen when we create a 4-H programs folder
def createProgram(subsite, programs, program_id, program_name, county_name="County Name"):
    urltool = getToolByName(subsite, 'portal_url')
    programs.invokeFactory(type_name='Folder', id=program_id, title=program_name)
    program_folder = programs[program_id]
    program_folder.unmarkCreationFlag()
    program_folder.setExcludeFromNav(True)
    program_folder.reindexObject()

    # Set restrictions 
    program_folder.setConstrainTypesMode(1) # restrict what this folder can contain
    program_folder.setImmediatelyAddableTypes(['Link','Folder','File','Document'])
    program_folder.setLocallyAllowedTypes(['Link','Folder','File','Document','Topic','Photo Folder','Blog','HomePage'])

    program_content = []
    
    if program_id == '4-h':
        program_content = [
            ['join', 'Document', 'Join', ''],
            ['volunteers', 'Folder', 'For Volunteers', ''],
            ['members', 'Folder', 'For Members', ''],
            ['clubs', 'Folder', 'Our Clubs', ''],
            ['about', 'Folder', 'About Us', ''],
            ['donate', 'Document', 'Donate to 4-H', ''],
            ['events', 'Topic', 'Upcoming Events', ''],
            ['news', 'Blog', 'News', ''],
            ['default', 'HomePage', '%s County 4-H' % county_name, ''],
        ]

    for (id, type_name, title, description) in program_content:
        if id not in program_folder.objectIds():
            program_folder.invokeFactory(type_name=type_name, id=id, title=title, description=description)
            program_folder[id].unmarkCreationFlag()
            
            this_obj = program_folder[id]
            
            # Create events collection
            if id == 'events':
                # Set the criteria for the folder
                type_crit = this_obj.addCriterion('Type','ATPortalTypeCriterion')
                
                type_crit.setValue(['Event']) # only our specified event types
                
                date_crit = this_obj.addCriterion('end', 'ATFriendlyDateCriteria')
                date_crit.setValue(0) # Set date reference to now
                date_crit.setDateRange('+') # Only list future events
                date_crit.setOperation('more')
                            
                # Set the county criteria
                county_crit = this_obj.addCriterion('Counties','ATSelectionCriterion')
                county_crit.setValue(county_name) # Only list events for the current county

                # Set the program criteria
                program_crit = this_obj.addCriterion('Programs','ATSelectionCriterion')
                program_crit.setValue(program_name) # Only list items in the current program
                
                sort_crit = this_obj.addCriterion('start','ATSortCriterion')
                
            if id == 'default':
                this_obj.setLayout('document_subsite_view')
                program_folder.setDefaultPage('default')
                # Set portlets for homepage
                homepage_centerColumn = getPortletAssignmentMapping(this_obj, 'agcommon.centercolumn')
                homepage_rightColumn = getPortletAssignmentMapping(this_obj, 'plone.rightcolumn')
        
                # Configure feedmixer news and events in center column
        
                # Grab path to news RSS feed, and make sure it's http://        
                program_news_rss = program_folder.absolute_url().replace('https:', 'http:') + '/news/latest/RSS'
                program_events_rss = program_folder.absolute_url().replace('https:', 'http:') + '/events/RSS'
                
                program_news = feedmixer.portlet.Assignment(
                            title="%s County %s News" % (county_name, program_name),
                            feeds=program_news_rss,
                            items_shown=5,
                            show_header=True,
                            show_date=True,
                            show_summary=True,
                            show_image=False,
                            show_footer=False,
                            cache_timeout=1800,
                            assignment_context_path=None)
                            
                saveAssignment(homepage_centerColumn, program_news)

                program_events = feedmixer.portlet.Assignment(
                            title="Upcoming Events",
                            feeds=program_events_rss,
                            items_shown=5,
                            show_header=True,
                            show_date=True,
                            show_summary=True,
                            show_image=False,
                            show_footer=False,
                            cache_timeout=1800,
                            assignment_context_path=None)
                            
                saveAssignment(homepage_centerColumn, program_events)

                # Put a person portlet as contact in the right column
                contact_portlet = person.Assignment(
                            header="Contact Us",
                            show_header=True,
                            people="abc123",
                            show_address=True,
                            show_image=False)
                            
                saveAssignment(homepage_rightColumn, contact_portlet)

                # 4-H Specific Front Page Portlets
                if program_id == '4-h':
                    # Put the general 4-h info RSS portlet in the right column
                    general_info = feedmixer.portlet.Assignment(
                            title="General 4-H Information",
                            feeds="http://extension.psu.edu/4-h/general-info/RSS",
                            items_shown=100,
                            show_header=True,
                            show_date=False,
                            show_summary=False,
                            show_image=False,
                            show_footer=False,
                            cache_timeout=1800,
                            assignment_context_path=None)
                            
                    saveAssignment(homepage_rightColumn, general_info)

            # 4-H Volunteers portlets
            if program_id == '4-h' and id == 'volunteers':

                volunteers_rightColumn = getPortletAssignmentMapping(this_obj, 'plone.rightcolumn')

                # Put the general 4-h info RSS portlet in the right column
                statewide_forms = feedmixer.portlet.Assignment(
                        title="State-Wide Volunteer Forms",
                        feeds="http://extension.psu.edu/4-h/leaders/forms/default/RSS",
                        items_shown=100,
                        show_header=True,
                        show_date=False,
                        show_summary=False,
                        show_image=False,
                        show_footer=False,
                        cache_timeout=1800,
                        assignment_context_path=None)
                        
                saveAssignment(volunteers_rightColumn, statewide_forms)
                
    
                # Put the general 4-h info RSS portlet in the right column
                leader_resources = feedmixer.portlet.Assignment(
                        title="Leader Resources",
                        feeds="http://extension.psu.edu/4-h/volunteer-leader-resources/RSS",
                        items_shown=100,
                        show_header=True,
                        show_date=False,
                        show_summary=False,
                        show_image=False,
                        show_footer=False,
                        cache_timeout=1800,
                        assignment_context_path=None)
                        
                saveAssignment(volunteers_rightColumn, leader_resources)
            # News
            if id == 'news':
                onBlogCreation(this_obj, None)

            # About Staff
            if id == 'about':

                this_obj.invokeFactory(type_name="Topic", id="staff", title="Our Staff", itemCount=99999)

                smart_obj = this_obj['staff']
                smart_obj.setLayout('folder_summary_view')
                smart_obj.unmarkCreationFlag()
            
                # Set the criteria for the folder
                type_crit = smart_obj.addCriterion('Type','ATPortalTypeCriterion')
                type_crit.setValue(['Person']) # only our specified event types
                
                # Set the county criteria
                county_crit = smart_obj.addCriterion('Counties','ATSelectionCriterion')
                county_crit.setValue(county_name) # Only list events for the current county

                # Set the program criteria
                program_crit = smart_obj.addCriterion('Programs','ATSelectionCriterion')
                program_crit.setValue(program_name) # Only list items in the current program
                
                sort_crit = smart_obj.addCriterion('getSortableName','ATSortCriterion')
            
            