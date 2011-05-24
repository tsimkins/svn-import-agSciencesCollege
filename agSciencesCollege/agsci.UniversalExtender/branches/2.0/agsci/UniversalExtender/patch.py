from Acquisition import aq_base, aq_inner
from Products.CMFCore.utils import getToolByName

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
    if theDate.startswith('0'):
        theDate = theDate.replace('0', '', 1)

    return theDate.replace(' 0', ' ')
    
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
