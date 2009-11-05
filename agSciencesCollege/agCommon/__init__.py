# Register our skins directory - this makes it available via portal_skins.

from Products.CMFCore.utils import getToolByName
from Products.CMFCore.DirectoryView import registerDirectory
from Products.PythonScripts.Utility import allow_module
from subprocess import Popen,PIPE
from zLOG import LOG, INFO

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

# Given start and end colors (optionally width and height) returns a gradient png

def gradientBackground(request):
    
    startColor = request.form.get("startColor", '000000')
    endColor = request.form.get("endColor", 'FFFFFF')
    
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
        startColor = '000000'
    
    if not re.match(colorRegex, endColor):
        endColor = 'FFFFFF'
    
    png = Popen(['convert', '-size', '%sx%s'%(width, height), 'gradient:#%s-#%s'%(str(startColor), str(endColor)), 'png:-'], stdout=PIPE)

    return "".join(png.stdout.readlines())


# Given a context, gets a list of all images and returns a JavaScript snippet
# that randomly picks one of them.
#
# To set an alignment (left, right) set a property of "align" on the image object.
# Otherwise, it defaults to center.

def getHomepageImage(context):
    backgrounds = []
    backgroundAlignments = []
    backgroundHeights = []
    
    for myImage in context.listFolderContents(contentFilter={"portal_type" : "Image"}):
        backgrounds.append(myImage.absolute_url())
    
        if myImage.hasProperty("align"):
            backgroundAlignments.append(myImage.align)
        else:
            backgroundAlignments.append("center")
    
        backgroundHeights.append(str(myImage.getHeight()))
        
    
    if not len(backgrounds):
        backgrounds = ['homepage_placeholder.jpg']
        backgroundAlignments = ['left']
        backgroundHeights = ['265']
    
    return """
    var bodyClass = document.body.className;
    
    if(bodyClass.match(/template-document_homepage_view/))
    {
        var homepageImage = document.getElementById("homepageimage");
    
        if (homepageImage)
        {
            var backgrounds = "%s".split(";");
            var backgroundAlignments = "%s".split(";");
            var backgroundHeights = "%s".split(";");
            var randomnumber = Math.floor(Math.random()*backgrounds.length) ;
            homepageImage.style.backgroundImage = "url(" + backgrounds[randomnumber] + ")";
            homepageImage.style.backgroundPosition = backgroundAlignments[randomnumber];
            homepageImage.style.height = backgroundHeights[randomnumber] + 'px';
        }
    
    }
    
    """ % (";".join(backgrounds), ";".join(backgroundAlignments), ";".join(backgroundHeights))

def makeHomePage(context):
    print context.portal_type
    print context.archetype_name
    context.archetype_name = 'Home Page'
    context.portal_type = 'HomePage'
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
def getPloneSites(context):

    ploneSites = []

    for myKey in context.keys():
        myChild = getattr(context, myKey)

        try:
            myType = myChild.getPortalTypeName()

        except AttributeError:
           pass

        else:
           if myType == 'Plone Site':
               ploneSites.append(myChild)

    return ploneSites

# Bulk reinstall agCommon and agCommonPolicy on all Plone sites
def reinstallAgCommon(context):

    toInstall = [
            'agCommon', 'agCommonPolicy', 
    ]

    #for site in getPloneSites(context):
    
    # Skip Extension, it has errors for some reason?
    #if ['extension.psu.edu', 'thinkagain.psu.edu'].count(site['id']):
    #    LOG('agCommon', INFO, "-----------Skipping %s because it throws errors." % site['id'])
    #    continue

    site = context
    qi = getToolByName(site, 'portal_quickinstaller')
    
    toReinstall = []

    for product in toInstall:
    
        LOG('agCommon', INFO, "Attempting to install %s on site %s" % (product, site.get('id', 'Unknown')))
    
        if not qi.isProductInstalled(product):
            if qi.isProductInstallable(product):
                try:
                    qi.installProduct(product)
                    LOG('agCommon', INFO,  "Installed product %s" % product)
                except WorkflowException:
                    LOG('agCommon', INFO,  "Workflow is in single state.  This causes an error.")
            else:
                LOG('agCommon', INFO,  "Product %s not installable" % product)
        else:
            LOG('agCommon', INFO,  "Product %s already installed -- Must reinstall." % product  )
            toReinstall.append(product)  
            
    qi.reinstallProducts(toReinstall)
