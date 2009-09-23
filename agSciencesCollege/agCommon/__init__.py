# Register our skins directory - this makes it available via portal_skins.

from Products.CMFCore.DirectoryView import registerDirectory
from subprocess import Popen,PIPE
import re

GLOBALS = globals()
registerDirectory('skins', GLOBALS)

def gradientBackground(request):
    
    startColor = request.form.get("startColor", '000000')
    endColor = request.form.get("endColor", 'FFFFFF')
    
    try:
        height = str(int(request.form.get("height", '600')))
    except ValueError:
        height = '600';
    
    # Validate we have a color code
    colorRegex = "^[0-9A-Fa-f]{3,6}$"
    
    if not re.match(colorRegex, startColor):
        startColor = '000000'
    
    if not re.match(colorRegex, endColor):
        endColor = 'FFFFFF'
    
    png = Popen(['convert', '-size', '8x%s'%height, 'gradient:#%s-#%s'%(str(startColor), str(endColor)), 'png:-'], stdout=PIPE)

    return "".join(png.stdout.readlines())