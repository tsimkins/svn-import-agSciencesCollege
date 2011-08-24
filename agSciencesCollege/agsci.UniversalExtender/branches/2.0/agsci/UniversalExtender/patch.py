from Acquisition import aq_base, aq_inner
from Products.CMFCore.utils import getToolByName
from Products.agCommon.browser.views import AgCommonUtilities

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
    
        return theDate.replace(' 0', ' ')
    else:
        return None
    
def collection_url(self):
    collection = self.collection()
    if collection is None:
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
