from Products.CMFCore.interfaces import ISiteRoot
from Products.CMFCore.utils import getToolByName
from Products.Five import BrowserView
from interfaces import IDepartmentExtenderUtilities, IResearchExtender
from zope.interface import implements

class DepartmentExtenderUtilities(BrowserView):

    implements(IDepartmentExtenderUtilities)

    # Checks to see if 'Faculty' is in one of the person's classifications.
    # Used for a field condition in agsci.DepartmentExtender
    def isFaculty(self, o):
        if o.portal_type in ['FSDPerson']:
            for c in o.getClassifications():
                if 'faculty' in c.Title().lower():
                    return True
            
        return False

    # Show research areas if the 'research_fields' boolean property is set in
    # /portal_properties/agcommon_properties, and one of the parents of the
    # object implement IResearchExtender
    # Used for a field condition in agsci.DepartmentExtender
    def showResearchAreas(self, o):
        ptool = getToolByName(o, 'portal_properties')
        props = ptool.get("agcommon_properties")

        if props.getProperty('research_fields', False):
            for i in o.aq_chain[1:]:
                if ISiteRoot.providedBy(i):
                    break
                elif IResearchExtender.providedBy(i):
                    return True 
        
        return False