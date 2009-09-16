from cStringIO import StringIO
from Products.CMFCore.DirectoryView import addDirectoryViews
from Products.CMFCore.utils import getToolByName
from Products.Archetypes.Extensions.utils import install_subskin
import os, string

from Products.PloneLightboxJS.config import *

def install(self):
    """Install Plone Lightbox JS: Install skin layer, javascript and
    stylesheet
    """
    out = StringIO()

    print >> out, "Installing %s" % PROJECTNAME

    # Install skin
    install_subskin(self, out, GLOBALS)
    print >> out, "Installed skin"

    # Register stylesheet
    csstool = getToolByName(self, 'portal_css')
    csstool.registerStylesheet(id='lightbox.css', media='screen')
	
    print >> out, "Registered stylesheet"

    print >> out, "Installation completed."
    return out.getvalue()

def uninstall(self):
    out = StringIO()

    skins_tool = getToolByName(self, 'portal_skins')
    skins = skins_tool.getSkinSelections()

    for skin in skins:
        path = skins_tool.getSkinPath(skin)
        path = [p.strip() for p in path.split(',') if p]
        while SKINNAME in path:
            path.remove(SKINNAME)
        skins_tool.addSkinSelection(skin, ','.join(path))

    print >> out, "Uninstalled skin"

    print >> out, "Uninstalling %s" % PROJECTNAME
    return out.getvalue()
