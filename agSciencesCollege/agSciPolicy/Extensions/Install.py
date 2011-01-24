from Products.CMFCore.utils import getToolByName

def install(portal):
    setup_tool = getToolByName(portal, 'portal_setup')
    setup_tool.runAllImportStepsFromProfile('profile-Products.agSciPolicy:default')
    return "Ran all import steps."

def uninstall(portal):
    return "No uninstall steps."
