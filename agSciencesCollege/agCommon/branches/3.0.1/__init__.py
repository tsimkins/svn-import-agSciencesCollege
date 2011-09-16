# Register our skins directory - this makes it available via portal_skins.

from zope.component import getSiteManager
from Products.CMFCore.utils import getToolByName
from Products.CMFCore.DirectoryView import registerDirectory
from Products.PythonScripts.Utility import allow_module
from zope.component.interfaces import ComponentLookupError
from Products.CMFCore.WorkflowCore import WorkflowException
from subprocess import Popen,PIPE
from zLOG import LOG, INFO, ERROR

import re

GLOBALS = globals()
registerDirectory('skins', GLOBALS)

# Allow us to use this module in scripts

allow_module('Products.agCommon')
allow_module('feedparser')
allow_module('datetime')
allow_module('datetime.datetime')
allow_module('Products.feedSync')
allow_module('Products.feedSync.sync')
allow_module('Products.feedSync.cvent')
allow_module('Products.feedSync.cvent.importEvents')
allow_module('Products.CMFCore.utils')
allow_module('Products.CMFCore.utils.getToolByName')
allow_module('urllib2')
allow_module('urllib')
allow_module('zope.component')
allow_module('zope.component.getSiteManager')

allow_module('Products.GlobalModules')
allow_module('Products.GlobalModules.makeHomePage')
allow_module('Products.GlobalModules.makePhotoFolder')
allow_module('Products.GlobalModules.fixPhoneNumber')

allow_module('ZODB.POSException')
allow_module('ZODB.POSException.POSKeyError')

allow_module('re')
allow_module('re.sub')
allow_module('re.compile')

# Precompile phoneRegex
phoneRegex = re.compile(r"^\((\d{3})\)\s+(\d{3})\-(\d{4})$")

#Ploneify
def ploneify(toPlone, isFile=False):
    if not isFile:
        ploneString = re.sub("[^A-Za-z0-9]+", "-", toPlone).lower()
    else:
        ploneString = re.sub("[^A-Za-z0-9\.]+", "-", toPlone).lower()
    ploneString = re.sub("-$", "", ploneString)
    ploneString = re.sub("^-", "", ploneString)
    return ploneString

# Given start and end colors (optionally width and height) returns a gradient png

def gradientBackground(request):
    
    startColor = request.form.get("startColor", 'FFFFFF')
    endColor = request.form.get("endColor")
    orientation = request.form.get("orientation", 'v').lower()[0]
    
    try:
        height = str(int(request.form.get("height", '600')))
    except ValueError:
        height = '600';

    try:
        width = str(int(request.form.get("width", '1')))
    except ValueError:
        width = '1';
    
    # Validate we have a color code
    colorRegex = "^[0-9A-Fa-f]{3,6}$"
    
    if not re.match(colorRegex, startColor):
        startColor = 'FFFFFF'

    def subtract_percent(s, p=20):
    
        if p > 100:
            p=100
            
        if p < 0:
            p=0
    
        dec = int(s, 16) * (100-p)/100
        return str('%X' % int(dec)).zfill(2)

    def split_rgb(s):
        d = {}
        d['r'] = s[0:2]
        d['g'] = s[2:4]
        d['b'] = s[4:7]
        return d
    
    def sum_colors(d):
        return sum(d.values())
    
    def calc(d, c):
        v = d[c]
        
        v_percent = float(sum([int(x, 16) for x in d.values()]))/(3*255)

        v_modify = 1

        if v_percent >= .6 or v_percent <= .3:
            v_modify = .8

        if v == min(d.values()):
            return subtract_percent(v, 70*v_modify)
        elif v == max(d.values()):
            return subtract_percent(v, 20*v_modify)
        else:
            return subtract_percent(v, 50*v_modify)
                        
    if not endColor or not re.match(colorRegex, endColor):
        colors = split_rgb(startColor)
        
        endColor = '%s%s%s' % (calc(colors,'r'), calc(colors,'g'), calc(colors,'b'))

    if orientation == 'h': 
        png = Popen(['convert', '-size', '%sx%s'%(height, width), 'gradient:#%s-#%s'%(str(startColor), str(endColor)), '-rotate', '270', 'png:-'], stdout=PIPE)
    else:
        png = Popen(['convert', '-size', '%sx%s'%(width, height), 'gradient:#%s-#%s'%(str(startColor), str(endColor)), 'png:-'], stdout=PIPE)

    return "".join(png.stdout.readlines())

# This is our multiple stripe main background
# Blackberries couldn't read the snazzy CSS way we did it, so it's now an ImageMagick script

def bodyBackground(context, request):
    
    portal_skins = getToolByName(context, 'portal_skins')

    try:
        width = str(int(request.form.get("width", '1')))
    except ValueError:
        width = '1';
    
    try:
        base_properties = portal_skins.custom.base_properties
    except AttributeError:
        base_properties = portal_skins.agcommon_styles.base_properties

    stripe_1 = base_properties.getProperty('backgroundStripeOneColor')
    stripe_2 = base_properties.getProperty('backgroundStripeTwoColor')
    stripe_3 = base_properties.getProperty('backgroundStripeThreeColor')
    background = base_properties.getProperty('bodyBackgroundColor')

    heights = [65,10,29,300,600]
    colors = [stripe_1, stripe_2, stripe_3, stripe_2]

    arguments = ['convert', '-size', '%sx%s' % (width, heights[-1]), 'gradient:%s-%s' % (stripe_2, background), 
                    '-gravity', 'south', '-extent', '%sx%s' % (width, sum(heights))]

    top_px = 0

    for i in range(0,len(colors)):
        arguments.extend(['-draw', 'fill %s rectangle 0,%s %s,%s' % (colors[i], top_px, width, top_px+heights[i])])
        top_px = top_px + heights[i]
        
    arguments.append('png:-')
    
    png = Popen(arguments, stdout=PIPE)
    return png.stdout.read()
    
    
# Given a context, gets a list of all images and returns a JavaScript snippet
# that randomly picks one of them.
#
# To set an alignment (left, right) set a property of "align" on the image object.
# Otherwise, it defaults to center.

def getHomepageImage(context):

    (backgrounds, backgroundAlignments, backgroundHeights) = getBackgroundImages(context, maxHeight=265)
    
    if not len(backgrounds):
        backgrounds = ['homepage_placeholder.jpg']
        backgroundAlignments = ['left']
        backgroundHeights = ['265']
    
    return """

    jq(document).ready(
        function () {
            homepageImage = jq("body.template-document_homepage_view #homepageimage");
            if (homepageImage)
            {
                var backgrounds = "%s".split(";");
                var backgroundAlignments = "%s".split(";");
                var backgroundHeights = "%s".split(";");
                var randomnumber = Math.floor(Math.random()*backgrounds.length);
    
                homepageImage.css('background-image', "url(" + backgrounds[randomnumber] + ")");
                homepageImage.css('background-position', backgroundAlignments[randomnumber] + " top");
                homepageImage.css("height", backgroundHeights[randomnumber] + 'px');
    
                jq("body.template-document_homepage_view #homepageimage div.overlay").each(
                    function () {
                        jq(this).css("height", backgroundHeights[randomnumber] + 'px');
                    }
                );
                
            }
        }
    );
    
    """ % (";".join(backgrounds), ";".join(backgroundAlignments), ";".join(backgroundHeights))

def getPortletHomepageImage(context, homepage_type="portlet"):
    return getPanoramaHomepageImage(context, homepage_type="portlet")

def getPanoramaHomepageImage(context, homepage_type="panorama"):

    (backgrounds, backgroundAlignments, backgroundHeights) = getBackgroundImages(context, maxHeight=250)
    
    if len(backgrounds):
    
        return """
    portalColumns = jq("body.template-%(homepage_type)s_homepage_view #portal-columns");
    visualPortalWrapper = jq("body.template-%(homepage_type)s_homepage_view #visual-portal-wrapper");
    breadcrumbs = jq("body.template-%(homepage_type)s_homepage_view #portal-breadcrumbs");
    
    if (portalColumns && visualPortalWrapper)
    {
        var backgrounds = "%(backgrounds)s".split(";");
        var backgroundAlignments = "%(alignments)s".split(";");
        var backgroundHeights = "%(heights)s".split(";");
        var randomnumber = Math.floor(Math.random()*backgrounds.length) ;

        var homepageImage = jq('<div id="panorama-homepage-image"><!-- --></div>');
        
        homepageImage.insertBefore(portalColumns);
        
        homepageImage.css("backgroundImage", "url(" + backgrounds[randomnumber] + ")");
        homepageImage.css("backgroundPosition", backgroundAlignments[randomnumber] + " top");
        homepageImage.css("paddingTop", backgroundHeights[randomnumber] + 'px');

        if (breadcrumbs)
        {
            breadcrumbs.detach();
            breadcrumbs.insertBefore(homepageImage);
        }
    }
    
    """ % {'homepage_type' : homepage_type, 'backgrounds' :  ";".join(backgrounds), 'alignments' : ";".join(backgroundAlignments), 'heights' : ";".join(backgroundHeights)}

def getSubsiteHomepageImage(context):

    (backgrounds, backgroundAlignments, backgroundHeights) = getBackgroundImages(context, maxHeight=188)
    
    if len(backgrounds):
    
        return """
        var homepageImage = jq('#image-header');        

        var backgrounds = "%(backgrounds)s".split(";");
        var backgroundAlignments = "%(alignments)s".split(";");
        var backgroundHeights = "%(heights)s".split(";");
        var randomnumber = Math.floor(Math.random()*backgrounds.length) ;
        
        homepageImage.css("backgroundImage", "url(" + backgrounds[randomnumber] + ")");
        homepageImage.css("backgroundPosition", backgroundAlignments[randomnumber] + " top");
        homepageImage.css("paddingTop", backgroundHeights[randomnumber] + 'px');

   
    """ % {'backgrounds' :  ";".join(backgrounds), 'alignments' : ";".join(backgroundAlignments), 'heights' : ";".join(backgroundHeights)}


def getBackgroundImages(context, maxHeight=265):
    backgrounds = []
    backgroundAlignments = []
    backgroundHeights = []
    
    for myImage in context.listFolderContents(contentFilter={"portal_type" : "Image"}):
        backgrounds.append(myImage.absolute_url())
    
        if myImage.hasProperty("align"):
            backgroundAlignments.append(myImage.align)
        else:
            backgroundAlignments.append("left")
        
        imageHeight = int(myImage.getHeight())
        
        if imageHeight > maxHeight:
            imageHeight = maxHeight
    
        backgroundHeights.append(str(imageHeight))
        
    return (backgrounds, backgroundAlignments, backgroundHeights)

def makePage(context):
    print context.portal_type
    print context.archetype_name
    context.archetype_name = 'Page'
    context.portal_type = 'Document'
    context.setLayout("document_view")
    context.reindexObject()
    print context.portal_type
    print context.archetype_name
    print "OK"

def makeHomePage(context):
    print context.portal_type
    print context.archetype_name
    context.archetype_name = 'Home Page'
    context.portal_type = 'HomePage'
    context.setLayout("document_homepage_view")
    context.reindexObject()
    print context.portal_type
    print context.archetype_name
    print "OK"

def makePhotoFolder(context):
    print context.portal_type
    print context.archetype_name
    context.archetype_name = 'Photo Folder'
    context.portal_type = 'PhotoFolder'
    context.reindexObject()
    print context.portal_type
    print context.archetype_name
    print "OK"

def folderToPage(folder):
    # Title, Description, Body Text, Author, Tags, Effective Date
    portal = getSiteManager(folder)
    wftool = getToolByName(portal, "portal_workflow")
    
    folder_id = folder.id
    folder_title = folder.Title()
    folder_description = folder.Description()
    folder_text = folder.folder_text()
    folder_owner = folder.getOwner()
    folder_subject = folder.Subject()
    folder_effective_date = folder.EffectiveDate()

    if wftool.getInfoFor(folder, 'review_state') != 'private':
        wftool.doActionFor(folder, 'retract')

    folder_parent = folder.getParentNode()
    
    folder_parent.manage_renameObject(folder_id, '%s-folder' % folder_id)
    
    folder_parent.invokeFactory(id=folder_id, type_name="Document", title=folder_title, description = folder_description, text=folder_text, subject=folder_subject)
    
    page = getattr(folder_parent, folder_id)
        
    page.changeOwnership(folder_owner)
    
    page.setEffectiveDate(folder_effective_date)

    if wftool.getInfoFor(page, 'review_state') != 'published':
        wftool.doActionFor(page, 'publish')
        
    page.reindexObject()
    
def pageToFolder(page):
    # Title, Description, Body Text, Author, Tags, Effective Date

    portal = getSiteManager(page)
    wftool = getToolByName(portal, "portal_workflow")
    
    page_id = page.id
    page_title = page.Title()
    page_description = page.Description()
    page_text = page.getText()
    page_owner = page.getOwner()
    page_subject = page.Subject()
    page_effective_date = page.EffectiveDate()

    if wftool.getInfoFor(page, 'review_state') != 'private':
        wftool.doActionFor(page, 'retract')
    
    page_parent = page.getParentNode()
    
    page_parent.manage_renameObject(page_id, '%s-page' % page_id)

    page_parent.invokeFactory(id=page_id, type_name="Folder", title=page_title, description = page_description, text=page_text, subject=page_subject)
    
    folder = getattr(page_parent, page_id)
        
    folder.changeOwnership(page_owner)
    
    folder.setEffectiveDate(page_effective_date)

    if wftool.getInfoFor(folder, 'review_state') != 'published':
        wftool.doActionFor(folder, 'publish')

    folder.reindexObject()
    
    
def fixPhoneNumber(myPerson):

    phone = myPerson.getOfficePhone()
    newPhone = phoneRegex.sub(r"\1-\2-\3", phone)

    if newPhone != phone:
        myPerson.setOfficePhone(newPhone)
        myPerson.reindexObject()
        return "%s: from %s to %s" % (myPerson.id, phone, newPhone)
    else:
        return "%s: Phone OK" % myPerson.id

# Intended to be used at the site root.  Returns a list of Plone sites.
def getPloneSites(context, recursive=True):

    ploneSites = []

    for myKey in context.keys():
        myChild = getattr(context, myKey)

        try:
            myType = myChild.meta_type

        except AttributeError:
           pass

        else:
           if myType == 'Plone Site':
               ploneSites.append(myChild)
           elif recursive and myType == 'Folder':
               ploneSites.extend(getPloneSites(myChild, recursive=False))

    return ploneSites
    
# Reinstall agCommon and agCommonPolicy on Plone sites
def reinstallAgCommon(site):

    toInstall = [
            'agCommon', 'agCommonPolicy', 
    ]

  
    LOG('agCommon.reinstallAgCommon', INFO,  "-"*50  )  
    LOG('agCommon.reinstallAgCommon', INFO,  "Starting reinstall on %s" % site  )  
    LOG('agCommon.reinstallAgCommon', INFO,  "-"*50  )  
        
    try:
        qi = getToolByName(site, 'portal_quickinstaller')
    except AttributeError:
        LOG('agCommon.reinstallAgCommon', ERROR,  "AttributeError for portal_quickinstaller" )
        return False
        
    toReinstall = []

    for product in toInstall:
    
        LOG('agCommon.reinstallAgCommon', INFO, "Attempting to install %s on site %s" % (product, site.get('id', 'Unknown')))
    
        if not qi.isProductInstalled(product):
            if qi.isProductInstallable(product):
                try:
                    qi.installProduct(product)
                    LOG('agCommon.reinstallAgCommon', INFO,  "Installed product %s" % product)
                except WorkflowException, e:
                    LOG('agCommon.reinstallAgCommon', ERROR,  "WorkflowException: (Workflow is in single state).  This causes an error: %s" % e)
                except ComponentLookupError, e:
                    LOG('agCommon.reinstallAgCommon', ERROR,  "ComponentLookupError: %s" % e)
            else:
                LOG('agCommon.reinstallAgCommon', INFO,  "Product %s not installable" % product)
        else:
            LOG('agCommon.reinstallAgCommon', INFO,  "Product %s already installed -- Must reinstall." % product  )
            toReinstall.append(product)  

    try:
        qi.reinstallProducts(toReinstall)
        LOG('agCommon.reinstallAgCommon', INFO,  "Reinstalling products [%s]" % ", ".join(toReinstall)  )
    except ComponentLookupError, e:
        LOG('agCommon.reinstallAgCommon', ERROR,  "ComponentLookupError: %s" % e  )


def sortFolder(context):
    folderContents = context.listFolderContents()
    for obj in sorted(folderContents, key=lambda x: x.Title().lower(), reverse=True):
        context.moveObjectsToTop(ids=[obj.id])
    for obj in folderContents:
        obj.reindexObject()
        


# Replace from_tag with new_tag
def replaceTag(context, from_tag, to_tag):

    catalog = getToolByName(context, 'portal_catalog')
    results = catalog.searchResults({'Subject' : from_tag})
    items = [x.getObject() for x in catalog.searchResults({'Subject' : from_tag})]
    
    for item in items:
    
        tags = list(item.Subject())
       
        while tags.count(from_tag):
            tags.remove(from_tag)

        if not tags.count(to_tag):
            tags.append(to_tag)
    
        item.setSubject(tags)
        item.reindexObject()
            
    topics = [x.getObject() for x in catalog.searchResults({'portal_type' : 'Topic'})]
    
    for t in topics:
        for o in t.objectIds():
            if o.count('Subject'):
                
                tags = list(t[o].value)

                if from_tag in tags:
                    
                    while tags.count(from_tag):
                        tags.remove(from_tag)
            
                    if not tags.count(to_tag):
                        tags.append(to_tag)
                        
                    t[o].setValue(tuple(tags))
                    t[o].reindexObject()
    

