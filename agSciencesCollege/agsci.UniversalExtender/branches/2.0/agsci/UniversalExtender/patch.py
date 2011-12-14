from Acquisition import aq_base, aq_inner
from Products.CMFCore.utils import getToolByName
from Products.agCommon.browser.views import AgCommonUtilities
from zope.component import getMultiAdapter

def folderGetText(self):
    """Products.ATContentTypes.content.folder.ATFolder"""

    # Define self.folder_text

    # Acquisition.aq_base strips the acquisition layer from an object.
    # See: https://weblion.psu.edu/trac/weblion/wiki/OverridingPloneAcquisition
    self = aq_base(self)

    try:
        return self.folder_text
    except:
        return ''

def toLocalizedTime(self, time, long_format=None, time_only=None):
    """Convert time to localized time
    """
    context = aq_inner(self.context)
    util = getToolByName(context, 'translation_service')
    theDate = util.ulocalized_time(time, long_format, time_only, context=context,
                                domain='plonelocales', request=self.request)
                                
    if theDate:
        if theDate.startswith('0'):
            theDate = theDate.replace('0', '', 1)

        theDate = theDate.replace('12:00 AM', '').strip()

        return theDate.replace(' 0', ' ')
    else:
        return None
    
def collection_url(self):
    collection = self.collection()
    limit = self.data.limit
    self.portal_state = getMultiAdapter((self.context, self.request),
                                            name=u'plone_portal_state')
    if collection is None:
        return None
    elif limit and limit > 0 and self.portal_state.anonymous() and len(collection.queryCatalog()) <= limit:
        # Don't show a URL if there is a limit, the user is anonymous 
        # (so people managing through the "More..." link can still use it)
        # and number of items are under a limit
        return None
    else:
        parent = collection.getParentNode()
        if collection.id == parent.getDefaultPage():
            return parent.absolute_url()
        else:
            return collection.absolute_url()

def _standard_results(self):
    results = []
    collection = self.collection()
    if collection is not None:
        limit = self.data.limit
        if limit and limit > 0:
            # pass on batching hints to the catalog
            results = collection.queryCatalog(batch=True, b_size=limit)
            results = results._sequence
        else:
            results = collection.queryCatalog()
        
        if hasattr(collection, "order_by_id") and collection.order_by_id:
            agcommon_utilities = self.context.restrictedTraverse('@@agcommon_utilities')
            results = agcommon_utilities.reorderTopicContents(results, collection.order_by_id)
        
        if limit and limit > 0:
            results = results[:limit]

    # This verifies that collections have contents before displaying them.
    # Intended to work with county sites in order to only show counties with
    # [Events, People, etc.] in the collection.
    
    valid_results = []

    for r in results:
        if r.portal_type == 'Topic' and not len(r.getObject().queryCatalog()):
            continue
        valid_results.append(r)

    return valid_results

# The "UberSelectionWidget" used by the collection portlet (and soon to be used 
# by the FeedMixer portlet) annoyingly has a hardcoded limit of 20 results.  This
# sets that limit to 99999.  The reason?  We have 100+ Extension subsites, all
# with a a standard layout, and a collection of 'upcoming'.

def uber_limit_results():
    return 99999


# Monkeypatch for FSD to only show people in the 'active' workflow state.

def getPeople(self):
    """Return a list of people contained within this FacultyStaffDirectory."""
    portal_catalog = getToolByName(self, 'portal_catalog')
    results = portal_catalog(path='/'.join(self.getPhysicalPath()), portal_type='FSDPerson', depth=1, review_state='active')
    return [brain.getObject() for brain in results]
