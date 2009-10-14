# Register our skins directory - this makes it available via portal_skins.

from Products.CMFCore.DirectoryView import registerDirectory
from Products.PythonScripts.Utility import allow_module
from subprocess import Popen,PIPE
import re

GLOBALS = globals()
registerDirectory('skins', GLOBALS)

# Allow us to use this module in scripts

allow_module('Products.agCommon')

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


