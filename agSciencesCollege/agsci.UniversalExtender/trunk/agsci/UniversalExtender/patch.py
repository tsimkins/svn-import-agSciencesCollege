from Acquisition import aq_base, aq_inner, aq_chain, aq_acquire
from Products.CMFCore.utils import getToolByName
from zope.component import getMultiAdapter, queryUtility
from plone.app.portlets.portlets import base
from Products.CMFCore.interfaces import IFolderish
from Products.CMFPlone.interfaces import IPloneSiteRoot, INonStructuralFolder
from Acquisition import aq_base, aq_inner, aq_parent
from plone.registry.interfaces import IRegistry
from plone.app.discussion.interfaces import IDiscussionSettings
from interfaces import INoComments
from DateTime import DateTime
from plone.app.blob.interfaces import IBlobField
from Products.Archetypes.interfaces import IFileField, IImageField, ITextField

from agsci.subsite.content.interfaces import ITagRoot

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

def customTableContents(self):
    # Monkeypatching this function into the other content types so the viewlet works appropriately

    # Acquisition.aq_base strips the acquisition layer from an object.
    # See: https://weblion.psu.edu/trac/weblion/wiki/OverridingPloneAcquisition
    self = aq_base(self)

    try:
        return self.tableContents
    except:
        return False


def toLocalizedTime(self, time, long_format=None, time_only=None, end_time=None):
    """Convert time to localized time
    """
    context = aq_inner(self.context)
    util = getToolByName(context, 'translation_service')

    def friendly(d):
    
        if not d:
            return ''

        if d.startswith('0'):
            d = d.replace('0', '', 1)
        
        d = d.replace('12:00 AM', '').strip()
        
        return d.replace(' 0', ' ')

    if not time:
        return ''

    start_full_fmt = friendly(util.ulocalized_time(time, long_format, time_only, context=context,
                                domain='plonelocales', request=self.request))
    
    if end_time:

        end_full_fmt = friendly(util.ulocalized_time(end_time, long_format, time_only, context=context,
                                       domain='plonelocales', request=self.request))
        start = DateTime(time)
        end = DateTime(end_time)
        
        start_date_fmt = start.strftime('%Y-%m-%d')
        end_date_fmt = end.strftime('%Y-%m-%d')       

        start_time_fmt = start.strftime('%H:%M')
        end_time_fmt = end.strftime('%H:%M') 
         
        # If the same date
        if start_date_fmt == end_date_fmt:
            
            # If we want the long format, return [date] [time] - [time]
            if long_format:
                if start_time_fmt == end_time_fmt and (start_time_fmt == '00:00' or end_time_fmt == '00:00'):
                    return start_full_fmt
                elif start_time_fmt == '00:00':
                    return end_full_fmt
                elif end_time_fmt == '00:00':
                    return start_full_fmt
                else:
                    return '%s, %s - %s' % (self.toLocalizedTime(time), self.toLocalizedTime(time, time_only=1), self.toLocalizedTime(end_time, time_only=1))
            # if time_only
            elif time_only:
                if start_full_fmt and end_full_fmt:
                    if start_full_fmt == end_full_fmt:
                        return start_full_fmt
                    else:
                        return '%s - %s' % (start_full_fmt, end_full_fmt)
                elif start_full_fmt:
                    return start_full_fmt
                elif end_full_fmt:
                    return end_full_fmt 
                else:
                    return ''                  
            # Return the start date in short format
            else:
                return start_full_fmt
        else:
            default_repr = '%s to %s' % (friendly(start_full_fmt), friendly(end_full_fmt))
            if long_format:
                return default_repr
            elif time_only:
                if start_full_fmt and end_full_fmt:
                    if start_full_fmt == end_full_fmt:
                        return start_full_fmt
                    else:
                        return '%s - %s' % (start_full_fmt, end_full_fmt)
                elif start_full_fmt:
                    return start_full_fmt
                elif end_full_fmt:
                    return end_full_fmt 
                else:
                    return ''
            elif start.year() == end.year():
                if start.month() == end.month():
                    return '%s %d-%d, %d' % (start.strftime('%B'), start.day(), end.day(), start.year())
                else:
                    return '%s %d - %s %d, %d' % (start.strftime('%B'), start.day(), end.strftime('%B'), end.day(), start.year())
            else:
                return default_repr

    else:
        if start_full_fmt:
            return friendly(start_full_fmt)
        else:
            return ''
    
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
    try:
        classifications = aq_acquire(self, 'fsd_classifications', None)
    except AttributeError:
        classifications = []

    if classifications:

        uids = []

        for r in portal_catalog.searchResults({'portal_type' : 'FSDClassification', 'Title': classifications}):
            if r.Title in classifications:
                uids.append(r.UID)
        results = portal_catalog(path='/'.join(self.getPhysicalPath()), portal_type='FSDPerson', depth=1, review_state='active', getRawClassifications=uids)
    else:
        results = portal_catalog(path='/'.join(self.getPhysicalPath()), portal_type='FSDPerson', depth=1, review_state='active')

    return [brain.getObject() for brain in results]


# Add 'isLeftColumn' method to navigation portlet to get manager

def navigation_portlet_left_column(self):
    try:
        if self.data.__parent__.__portlet_metadata__.get('manager') == 'plone.leftcolumn':
            return True
        else:
            return False
    except AttributeError, KeyError:
        return False
        

# Change logic for comments being enabled

def commentsEnabled(self):
    # Returns True if discussion is enabled on the conversation
    # Note: self is the conversation object, parent is the Plone object
    # that contains the conversation

    # Fetch discussion registry
    registry = queryUtility(IRegistry)
    settings = registry.forInterface(IDiscussionSettings, check=False)

    # If discussion is not allowed globally, return False
    if not settings.globally_enabled:
        return False

    # parent is the object itself
    parent = aq_inner(self.__parent__)

    # Always return False if object provides the INoComments interface.
    # This would be for Subsites, Sections, 
    # Blogs and HomePages
    if (INoComments.providedBy(parent)):
        return False

    # obj is the parent with different acquisition wrappings
    obj = aq_parent(self)

    # Check if discussion is allowed on the content type
    portal_types = getToolByName(self, 'portal_types')
    document_fti = getattr(portal_types, obj.portal_type)
    if document_fti.getProperty('allow_discussion'):
        # If discussion is allowed on the content type, return True
        return True

    def traverse_parents(o_obj):
        # Run through the aq_chain of obj and check if discussion is
        # enabled in a parent folder.  Stops at the Plone Site level.
        # Stops at the Section/Subsite/Blog level because they implement INoComments
        for obj in o_obj.aq_chain:
            if IPloneSiteRoot.providedBy(obj):
                return False
            elif IFolderish.providedBy(obj) and getattr(aq_base(obj), 'allow_discussion_contents', False):
                return True
            elif INoComments.providedBy(obj):
                return False
        return False

    # If discussion is enabled for the object, return True
    if getattr(aq_base(obj), 'allow_discussion', False):
        return True

    # Check if traversal found a folder with allow_discussion_contents 
    # set to True in the acquisition chain.
    if not IFolderish.providedBy(obj) and traverse_parents(obj):
        return True

    return False

def getAvailableTags(self):
    """Returns the 'available_public_tags' from the nearest object in the acquisition chain"""
    tags = []
    for i in aq_chain(self):
        if IPloneSiteRoot.providedBy(i):
            break
        if ITagRoot.providedBy(i):
            if hasattr(i, 'available_public_tags'):
                tags = getattr(i, 'available_public_tags')
            break
    return tags
    
def icon(self, portal_type):
    type = self.ttool.getTypeInfo(portal_type)

    default_icon = 'document_icon.png'

    if type is None:
        return None

    icon = type.getIcon()

    if not icon:
        icon = {
            'Document' : 'document_icon.png',
            'Event' : 'event_icon.png',
            'File' : 'file_icon.png',
            'Folder' : 'folder_icon.png',
            'Image' : 'image_icon.png',
            'Link' : 'link_icon.png',
            'News Item' : 'newsitem_icon.png',
            'Plone Site' : 'logoIcon.png',
            'TempFolder' : 'folder_icon.png',
            'Topic' : 'topic_icon.png',}.get(type.id, default_icon)

    return "%s/%s" % (self.base, icon)


def eventShortLocation(self):
    """Products.ATContentTypes.content.event.ATEvent"""

    if hasattr(self, 'zip_code'):
        zip = getattr(self, 'zip_code')
        if zip:
            try:
                ezt = getToolByName(self, "extension_zipcode_tool")
            except AttributeError:
                return None

            zipinfo = ezt.getZIPInfo(zip)
            
            if zipinfo:
                return zipinfo[1]

    return None