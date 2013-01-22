from zope.interface import implements, Interface
from Products.Five import BrowserView
from Products.CMFCore.utils import getToolByName
from Products.agCommon.browser.views import FolderView, AgendaView
from agsci.subsite.content.interfaces import ITagRoot
from plone.memoize.view import memoize
from zope.component import getUtility
from plone.i18n.normalizer.interfaces import IIDNormalizer
from Products.CMFPlone.interfaces import IPloneSiteRoot
from Acquisition import aq_chain, aq_acquire

class ITagsView(Interface):
    """
    tags view interface
    """

    def test():
        """ test method"""

class TagsView(AgendaView):

    implements(ITagsView)

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.url_tags = []
        
        # Overrite configuration
        self.singular_title = 'Tag'
        self.plural_title = 'Tags'

        self.tag_listing = 'available_public_tags'
        self.obj_tags = 'public_tags'
        self.target_view = 'tags'
        self.catalog_index = 'Tags'

    @property
    def portal_catalog(self):
        return getToolByName(self.context, 'portal_catalog')

    @property
    def normalizer(self):
        return getUtility(IIDNormalizer)

    def page_title(self):
        tags = self.tags

        if len(tags) > 1:
            title = self.plural_title
        else:
            title = self.singular_title
            
        return '%s (%s: %s)' % (self.context_state.object_title(), title, ', '.join(tags))
    
    def publishTraverse(self, request, name):

        if name:
            if '|' in name:
                self.url_tags = sorted(name.split('|'))
            else:
                self.url_tags = [name]
        else:
            self.url_tags = []

        self.original_url = request.getURL()
        self.original_context = self.context
        
        self.context = self.tag_root

        return self

    def getSettingsObject(self):
        obj = None

        try:
            default_page = self.original_context.getDefaultPage()
            if default_page in self.original_context.objectIds() and self.original_context[default_page].portal_type == 'Topic':
                obj = self.original_context[default_page]
        except:
            pass
            
        if not obj:
            obj = self.original_context
        
        return obj

    @property
    def listingLayout(self):
        try:
            layout = self.getSettingsObject().getLayout()
        except:
            layout = None

        if layout in ['agenda_view', 'atct_album_view', 'event_table', 'folder_listing', 'folder_summary_view', ]:
            return layout
        else:
            return 'folder_listing'

    @property
    def tag_root(self):

        for i in aq_chain(self.context):
            if IPloneSiteRoot.providedBy(i):
                return i
            if ITagRoot.providedBy(i):
                return i

        # Probably not needed, but just so we return something.
        return self.context
        
    @property
    def available_tags(self):

        available_tags = []

        tag_root = self.tag_root
        
        if hasattr(tag_root, self.tag_listing):
            available_tags = getattr(tag_root, self.tag_listing)        

        if not available_tags:
            available_tags = self.portal_catalog.uniqueValuesFor(self.catalog_index)
        
        return available_tags


    @property
    def tags(self):

        # Get the intersection of the tags provided in the URL and the tags
        # available to be used.
        
        available_tags = self.available_tags
        normalized_available_tags = [self.normalizer.normalize(x) for x in available_tags]

        item_tags = []

        for t in self.available_tags:
            if self.normalizer.normalize(t) in self.url_tags:
                item_tags.append(t)

        return item_tags

    def getFolderContents(self):
        tag_root = self.tag_root
        tags = self.tags

        if ITagRoot.providedBy(tag_root):
            default_page = tag_root.getDefaultPage()
            if default_page in tag_root.objectIds() and tag_root[default_page].portal_type == 'Topic':
                return tag_root[default_page].queryCatalog(**{self.catalog_index : tags})

            return []
        elif tags:
            return self.portal_catalog.searchResults({self.catalog_index : tags, 'path' : '/'.join(tag_root.getPhysicalPath())})
        else:
            return []

    @property
    def show_date(self):
        try:
            show_date = aq_acquire(self.getSettingsObject(), 'show_date')
        except AttributeError:
            show_date = False
        
        return show_date

    @property
    def show_image(self):
        try:
            show_image = aq_acquire(self.getSettingsObject(), 'show_image')
        except AttributeError:
            show_image = False
        
        return show_image

    @property
    def show_read_more(self):
        try:
            show_read_more = aq_acquire(self.getSettingsObject(), 'show_read_more')
        except AttributeError:
            show_read_more = False
        
        return show_read_more