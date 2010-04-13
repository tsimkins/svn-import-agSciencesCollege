# Create new members with properties supplied from a CSV file.
# The script expects a File object with id `users.csv` in the same folder
# it resides.
#
# The format of the CSV needs to be:
#
# password;userid;lastname;firstname;email
#
# created 2006-11-03 by Tom Lazar <tom@tomster.org>, http://tomster.org/
# under a BSD-style licence (i.e. use as you wish but don't sue me)

from zope.app.component.hooks import setSite
from zope.component import getSiteManager, getUtility, getMultiAdapter
from zope.component.interfaces import ComponentLookupError
from Products.CMFCore.utils import getToolByName
from plone.portlets.interfaces import IPortletManager, IPortletAssignmentMapping
from plone.app.viewletmanager.manager import ManageViewlets
from Products.CMFCore.WorkflowCore import WorkflowException
from zLOG import LOG, INFO
import os.path
import string
import random
import pdb

random.seed()

def createUsers(context):

    site = context.getSite()

    users = [
                ["trs22", "Simkins", "Tim", "trs22@psu.edu"],
                ["cjm49", "More", "Chris", "cjm49@psu.edu"],
                ["axd159", "Devlin", "Ann", "axd159@psu.edu"],
                ["mjw174", "Wodecki", "Mary", "mjw174@psu.edu"],
                ["pgw105", "Warren", "Pete", "pgw105@psu.edu"],
                ["tds194", "Sassman", "Tyler", "tds194@psu.edu"],
                ["gxa2", "Abdullah", "Gary", "gxa2@psu.edu"],
            ]

    printed = []
    sm = getSiteManager(site)
    regtool = getToolByName(sm, 'portal_registration')
    grouptool = getToolByName(sm, 'portal_groups')
    
    administratorsGroup = grouptool.getGroupById("Administrators")
    
    index = 1
    imported_count = 0
    
    for tokens in users:
    
        if len(tokens) == 4:
            id, last, first, email = tokens
            properties = {
                'username' : id,
                'fullname' : '%s %s' % (first, last),
                'email' : email.strip(),
                'visible_ids' : True
            }
            try:
                regtool.addMember(id, randomPassword(), properties=properties)
                printed.append("Successfully added %s %s (%s) with email %s" % (first, last, id, email))
                imported_count += 1
                
            except ValueError, e:
                printed.append("Couldn't add %s: %s" % (id, e))
    
    
            try:
            
                administratorsGroup.addMember(id) 
                printed.append("Successfully added %s to Administrators group" % (id))
                
            except:
    
                printed.append("Couldn't add %s to Administrators group" % (id))
    
        else:
            printed.append("Could not parse line %d because it had the following contents: '%s'" % (index, user))
        index += 1
    
    printed.append("Imported %d users (from %d total users)" % (imported_count, index))
    
    return "\n".join(printed)

def randomPassword():
    d = [random.choice(string.letters) for x in xrange(32)]
    s = "".join(d)
    return s

def deleteUnusedFolders(context):
    site = context.getSite()
    for theFolder in ['Members', 'news', 'events']:

        if theFolder in site.objectIds():

            theFolderObject = getattr(site, theFolder)
            if theFolderObject.getPortalTypeName() != 'Folder':            
                urltool = getToolByName(site, "portal_url")
                portal = urltool.getPortalObject()
                portal.manage_delObjects([theFolder])
                LOG('agCommonPolicy.deleteUnusedFolders', INFO, "deleted folder %s" % theFolder)
        else:
            LOG('agCommonPolicy.deleteUnusedFolders', INFO, "Folder %s not found" % theFolder)
            

def createSiteFolders(context):
    site = context.getSite()
    # Publish from http://svn.cosl.usu.edu/svndev/eduCommons3/branches/yale-3.0.2/setupHandlers.py
    wftool =  getToolByName(site, 'portal_workflow')

    for theArray in [['about', 'About Us'], ['news', 'News'], ['events', 'Events'], ['contact', 'Contact Us'], ['background-images', 'Background Images'], ['images', 'Images']]:
        (theId, theTitle) = theArray
        
        if theId not in site.objectIds():
            site.invokeFactory('Folder', id=theId, title=theTitle)
            
            theObject = getattr(site, theId)
            
            try:
                if wftool.getInfoFor(theObject, 'review_state') != 'Published':
                    wftool.doActionFor(theObject, 'publish')
            except WorkflowException:
                LOG('agCommonPolicy.createSiteFolders', INFO, "Site has no workflow, not publishing folder")
                
            if theId == 'background-images' or theId == 'images':
                theObject.setExcludeFromNav(True)
                theObject.reindexObject()

            LOG('agCommonPolicy.createSiteFolders', INFO, "Created and published folder %s" % theId)
        else:
            LOG('agCommonPolicy.createSiteFolders', INFO, "Folder %s already exists." % theId)
            
def configureFrontPage(context):
    site = context.getSite()

    if hasattr(site, 'front-page'):
        frontPage = getattr(site, 'front-page')
        
        try:
            type = frontPage.getPortalTypeName()
        except AttributeError:
            LOG('agCommonPolicy.configureFrontPage', INFO, "front-page has no function getPortalTypeName()")
        else:
            if type != 'HomePage':
                frontPage.setText('Home Page should be set to "Homepage View"')
                frontPage.setTitle('Home')
                frontPage.setDescription('')
                frontPage.setPresentation(False)
                frontPage.setLayout("document_homepage_view")
                frontPage.archetype_name = 'Home Page'
                frontPage.portal_type = 'HomePage'
                frontPage.reindexObject()

                LOG('agCommonPolicy.configureFrontPage', INFO, "Configured front-page")        

def setSitePortlets(context):

    site = context.getSite()

    LOG('agCommonPolicy.setSitePortlets', INFO, "Setting site portlets.")

    try:

        ploneLeftColumn = getUtility(IPortletManager, name=u'plone.leftcolumn', context=site)
        ploneLeft = getMultiAdapter((site, ploneLeftColumn), IPortletAssignmentMapping, context=site)

        ploneRightColumn = getUtility(IPortletManager, name=u'plone.rightcolumn', context=site)
        ploneRight = getMultiAdapter((site, ploneRightColumn), IPortletAssignmentMapping, context=site)
    
    except ComponentLookupError:
        LOG('agCommonPolicy.setSitePortlets', INFO, "ComponentLookupError")

    else:

        for deletePortlet in [u'review', u'news', u'events', u'calendar']:
            try:
                del ploneRight[deletePortlet]
                LOG('agCommonPolicy.setSitePortlets', INFO, "Deleted %s" % deletePortlet)
            except KeyError:
                LOG('agCommonPolicy.setSitePortlets', INFO, "No portlet named %s" % deletePortlet)
            
            
        for deletePortlet in [u'login']:
            try:
                del ploneLeft[deletePortlet]
                LOG('agCommonPolicy.setSitePortlets', INFO, "Deleted %s" % deletePortlet)
            except KeyError:
                LOG('agCommonPolicy.setSitePortlets', INFO, "No portlet named %s" % deletePortlet)

        if ploneLeft.has_key('navigation'):
            LOG('agCommonPolicy.setSitePortlets', INFO, "Set navigation portlet start level")
            ploneLeft['navigation'].topLevel = 0


def addExtensionToMimeType(registry, extension, mimetype):
    for myMime in registry.lookup(mimetype):
        glob = '*.%s' % extension
        registry.register_extension(extension, myMime)
        registry.register_glob(glob, myMime)

        newExtensions = list(myMime.extensions)
        newExtensions.append(extension)
        newExtensions = tuple(newExtensions)

        newGlobs = list(myMime.globs)
        newGlobs.append(glob)
        newGlobs = tuple(newGlobs)

        myMime.edit(myMime.name(), myMime.mimetypes, newExtensions, myMime.icon_path, globs=newGlobs)

        LOG('agCommonPolicy.addExtensionToMimeType', INFO, "Added extension %s to mimetype %s" % (extension, mimetype))

def configureMimeTypes(context):
    
    site = context.getSite()
    
    listOfMimeTypes = [
            ['docm', 'application/msword'],
            ['docx', 'application/msword'],
            ['dotm', 'application/msword'],
            ['dotx', 'application/msword'],
            ['potm', 'application/vnd.ms-powerpoint'],
            ['potx', 'application/vnd.ms-powerpoint'],
            ['ppam', 'application/vnd.ms-powerpoint'],
            ['ppsm', 'application/vnd.ms-powerpoint'],
            ['ppsx', 'application/vnd.ms-powerpoint'],
            ['pptm', 'application/vnd.ms-powerpoint'],
            ['pptx', 'application/vnd.ms-powerpoint'],
            ['xlam', 'application/vnd.ms-excel'],
            ['xlsb', 'application/vnd.ms-excel'],
            ['xlsm', 'application/vnd.ms-excel'],
            ['xlsx', 'application/vnd.ms-excel'],
            ['xltm', 'application/vnd.ms-excel'],
            ['xltx', 'application/vnd.ms-excel']
    ]

    mimetypes_registry = getattr(site, 'mimetypes_registry')

    for (extension, mimetype) in listOfMimeTypes:
         addExtensionToMimeType(mimetypes_registry, extension, mimetype)

def configureFSD(context):

    site = context.getSite()

    try:
        fsdtool = getToolByName(site, 'facultystaffdirectory_tool')
    except AttributeError:
        LOG('agCommonPolicy.configureFSD', INFO, "FSD not installed.")
    else:
        fsdtool.setPhoneNumberDescription('555-555-5555')
        fsdtool.setPhoneNumberRegex('^\d{3}-\d{3}-\d{4}$')
        fsdtool.setUseInternalPassword(False)
        LOG('agCommonPolicy.configureFSD', INFO, "Configured FSD")

def configureScripts(context):
    # We're going to copy the contents of scripts in agcommon_templates
    # to the root of the site, since we can't actually copy them as objects.

    LOG('agCommonPolicy.configureScripts', INFO, "Context: %s"  % context)

    site = context.getSite()
    portal_skins = getToolByName(site, 'portal_skins')

    LOG('agCommonPolicy.configureScripts', INFO, "Site: %s"  % site)
    
    toCopy = [
        { 
            'src' : 'getHomepageImage',
            'target' : 'getHomepageImage.js'
        },
        { 
            'src' : 'getPortletHomepageImage',
            'target' : 'getPortletHomepageImage.js'
        },
        { 
            'src' : 'gradientBackground',
            'target' : 'gradientBackground.png'
        },
        { 
            'src' : 'gradientBackground',
            'target' : 'topnav-gradientBackground.png'
        },
        { 
            'src' : 'gradientBackground',
            'target' : 'leftbutton-gradientBackground.png'
        },
        {
            'src' : 'gradientBackground',
            'target' : 'topnav-alternate-gradientBackground.png'
        },

    ]
    
    try:
        templates = portal_skins.agcommon_templates
        LOG('agCommonPolicy.configureScripts', INFO, 'templates: %s' % templates)
    except AttributeError:
        LOG('agCommonPolicy.configureScripts', INFO, "AttributeError Can't find agcommon_templates")
        LOG('agCommonPolicy.configureScripts', INFO, "----\n----".join(portal_skins.keys()))
    except KeyError:
        LOG('agCommonPolicy.configureScripts', INFO, "KeyError Can't find agcommon_templates")
    else:
    
        addPythonScript = site.manage_addProduct['PythonScripts'].manage_addPythonScript
    
        for script in toCopy:
            src = script['src']
            target = script['target']

            try:
                site.manage_delObjects([target])
                LOG('agCommonPolicy.configureScripts', INFO, "Deleted existing script %s" % target)
            except AttributeError:
                LOG('agCommonPolicy.configureScripts', INFO, "Site does not have script %s" % target)
        
            addPythonScript(target)
            
            newScript = getattr(site, target)
            packageScript = getattr(templates, src)            
            
            newScript.write(packageScript.read())
            
            site[target].ZCacheable_setManagerId('HTTPCache')
            
            LOG('agCommonPolicy.configureScripts', INFO, "Added script %s" % target)


# Install required products
# Borrowed from http://plone.org/documentation/faq/install-dependencies

def installAdditionalProducts(context):
    
    # This doesn't work, apparently gets called recursively?
    
    return False

    toInstall = [
            'CacheSetup', 'FacultyStaffDirectory', 'FolderText', 'WebServerAuth', 
            'agCommonPolicy', 'collective.contentleadimage', 'collective.portlet.feedmixer', 
            'plone.app.imaging', 'plonegalleryview'
    ]

    site = context.getSite()
    qi = getToolByName(site, 'portal_quickinstaller')

    for product in toInstall:
    
        LOG('agCommonPolicy.installAdditionalProducts', INFO, "Attempting to install %s" % product)
    
        if not qi.isProductInstalled(product):
            if qi.isProductInstallable(product):
                qi.installProduct(product)
                LOG('agCommonPolicy.installAdditionalProducts', INFO, "Installed product %s" % product)
            else:
                LOG('agCommonPolicy.installAdditionalProducts', INFO, "Product %s not installable" % product)
        else:
            LOG('agCommonPolicy.installAdditionalProducts', INFO, "Product %s already installed." % product)

# This will update the base_properties file to contain any new base_properties
# No more "white screen of death"

def updateBaseProperties(context):
    site = context.getSite()
    #pdb.set_trace()
    resetProperties = site.getParentNode().get('resetProperties', '').split()
    LOG('agCommonPolicy.updateBaseProperties', INFO, "Resetting %s" % ", ".join(resetProperties))
    
    # Let's give it a go!
    LOG('agCommonPolicy.updateBaseProperties', INFO, "Updating Base properties for %s" % site['id'])
    portal_skins = getattr(site, 'portal_skins')

    custom = getattr(portal_skins, 'custom')

    try:
        agcommon_styles = getattr(portal_skins, 'agcommon_styles')
    except:
        LOG('agCommonPolicy.updateBaseProperties', INFO, "ERROR: %s : agCommon skin not installed" % site['id'])
        return False
        
    try:
        custom_base_properties = getattr(custom, 'base_properties')
    except:
        LOG('agCommonPolicy.updateBaseProperties', INFO, "ERROR: %s : No customized base_properties" % site['id'])
        return False
        
    base_properties = getattr(agcommon_styles, 'base_properties')

    try:            
        for myProperty in base_properties.propertyItems():
            (myPropertyKey, myPropertyValue) = myProperty
            myPropertyType = base_properties.getPropertyType(myPropertyKey)

            if not custom_base_properties.getProperty(myPropertyKey):

                try:
                    custom_base_properties.manage_addProperty(myPropertyKey, myPropertyValue, myPropertyType)
                except:
                    LOG('agCommonPolicy.updateBaseProperties', INFO, "ERROR: %s : Error adding property %s:%s=%s" % (site['id'], myPropertyKey, myPropertyType, myPropertyValue))
                    return False
                    
                LOG('agCommonPolicy.updateBaseProperties', INFO, "Added %s:%s=%s" % (myPropertyKey, myPropertyType, myPropertyValue))

            elif resetProperties.count(myPropertyKey):
                try:
                    custom_base_properties.manage_changeProperties({myPropertyKey : myPropertyValue})
                except:
                    LOG('agCommonPolicy.updateBaseProperties', INFO, "ERROR: %s : Error updating property %s:%s=%s" % (myKey, myPropertyKey, myPropertyType, myPropertyValue))
                    continue
                    
                LOG('agCommonPolicy.updateBaseProperties', INFO, "Updated %s:%s=%s" % (myPropertyKey, myPropertyType, myPropertyValue))
                            
    except:
        LOG('agCommonPolicy.updateBaseProperties', INFO, "ERROR: %s : Problem updating properties" % site['id'])
                            

def customizeViewlets(context):
    
    site = context.getSite()
    
    if site['id'] == 'agsci.psu.edu':
        ManageViewlets.show('plone.portalfooter', 'contentwellportlets.portletsbelowcontent')

def createRecentChanges(context):

    # Creates a /recent-changes collection

    site = context.getSite()
    sm = getSiteManager(site)

    if hasattr(site, 'recent-changes'):
        site.manage_delObjects(['recent-changes'])
    
    # Create collection
    site.invokeFactory(id="recent-changes", type_name="Topic", title="Recent Changes")
    theCollection = getattr(site, "recent-changes")
    theCollection.setExcludeFromNav(True)

    wftool =  getToolByName(site, 'portal_workflow')

    try:
        if wftool.getInfoFor(theCollection, 'review_state') != 'Published':
            wftool.doActionFor(theCollection, 'publish')
    except WorkflowException:
        LOG('agCommonPolicy.createRecentChanges', INFO, "Site has no workflow, not publishing folder")

    # Modified date
    theCriteria = theCollection.addCriterion('modified', 'ATFriendlyDateCriteria')
    theCriteria.setOperation('less') # Less than
    theCriteria.setValue(7) # Seven days
    theCriteria.setDateRange('-') # in the past

    # Sort by modified date
    theCriteria = theCollection.addCriterion('modified','ATSortCriterion') 

    LOG('agCommonPolicy.createRecentChanges', INFO, "Adding 'recent-changes' collection")

def configureKupu(context):

    # addLibrary(self, id, title, uri, src, icon)
    # This puts the "images" folder

    site = context.getSite()
    sm = getSiteManager(site)
    kupu = getToolByName(sm, 'kupu_library_tool')
    
    has_images_library = False
    
    for lib in kupu.getLibraries(sm):
        if lib['id'] == 'images':
            has_images_library = True
            break
        
    if not has_images_library:
        kupu.addLibrary('images', 'string:Images', 'string:${portal_url}/images', 
            'string:${portal_url}/images/kupucollection.xml', 'string:${portal_url}/image_icon.gif')
        LOG('agCommonPolicy.configureKupu', INFO, "Adding 'images' Kupu library")
        
    # Set up the nasty/stripped/custom tags 
    # http://plone.org/documentation/how-to/how-to-embed-content-flickr-youtube-or-myspace
    """
    * Remove "Object" and "Embed" from the "Nasty Tags" list
    * Remove "Object" and "Param" from the "Stripped Tags" list
    * Add "Embed" to the "Custom Tags" list
    """
    
    # Grab data structures
    portal_transforms = site['portal_transforms']
    safe_html = portal_transforms['safe_html']   
    nasty_tags = safe_html.get_parameter_value('nasty_tags')     
    valid_tags = safe_html.get_parameter_value('valid_tags')
    
    # Make changes required to embed content
    if nasty_tags.get('object'):
        del nasty_tags['object']

    if nasty_tags.get('embed'):
        del nasty_tags['embed']
        
    valid_tags['object'] = 1
    valid_tags['embed'] = 1
    valid_tags['param'] = 1
    valid_tags['iframe'] = 1
        
    # Obtain key/value structures from dicts
    
    nasty_tags_key = []
    nasty_tags_value = []

    for key,value in nasty_tags.items():
        nasty_tags_key.append(key)
        nasty_tags_value.append(str(value))

    valid_tags_key = []
    valid_tags_value = []

    for key,value in valid_tags.items():
        valid_tags_key.append(key)
        valid_tags_value.append(str(value))

    # Load these structures into the safe_html object
    kwargs = {'nasty_tags_key': nasty_tags_key,'nasty_tags_value': nasty_tags_value,'valid_tags_key': valid_tags_key, 'valid_tags_value': valid_tags_value}
    safe_html.set_parameters(**kwargs)
    safe_html.reload()

    # True up the Kupu side of things
    stripped_tags = kupu.get_stripped_tags()
    stripped_tags = list(set(stripped_tags) - set(['object', 'param']))
    kupu.set_stripped_tags(stripped_tags)
    
    # Set embed-tab filter
    filteroptions = kupu.getFilterOptions()

    for f in filteroptions:
        if f["id"] == 'embed-tab':   
            f["visible"] = True
    
    kupu.set_toolbar_filters(filteroptions,kupu._global_toolbar_filter)

    LOG('agCommonPolicy.configureKupu', INFO, "Enabled embedding YouTube/etc. content")

def setupHandlersWrapper(context):

    if context.readDataFile('agCommonPolicy.marker') is None:
        LOG('agCommonPolicy.setupHandlersWrapper', INFO, "Not running setup handlers from a non-agCommonPolicy install")
        return
    
    site = context.getSite()

    installAdditionalProducts(context)

    createUsers(context)
    
    deleteUnusedFolders(context)
    
    createSiteFolders(context)

    configureFrontPage(context)
    
    setSitePortlets(context)

    configureMimeTypes(context)
    
    configureFSD(context)

    configureScripts(context)

    updateBaseProperties(context)
    
    configureKupu(context)
    
    createRecentChanges(context)

    #customizeViewlets(context)
        
 
