from zope.component import getUtility, getMultiAdapter
from zope.app.container.interfaces import INameChooser

from zLOG import LOG, INFO
from plone.portlets.interfaces import IPortletManager, IPortletAssignmentMapping, ILocalPortletAssignmentManager

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
    LOG('pugdemo.subsite', INFO, msg)
