from agsci.subsite.browser.views.tags import TagsView

class ResearchAreasView(TagsView):

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.url_tags = []

        # Overrite configuration
        self.singular_title = 'Research Area'
        self.plural_title = 'Research Area'

        self.obj_tags = 'department_research_areas'
        self.target_view = 'research-areas'
        self.catalog_index = 'department_research_areas'

    @property
    def parent_object(self):

        # parent_object is the portlet's parent
        # Default to self.context
        parent_object = self.context

        # If context is the default page, set parent_object to parentNode
        parentNode = self.context.getParentNode()

        if hasattr(parentNode, 'getDefaultPage') and parentNode.getDefaultPage() == self.context.getId():
            parent_object = parentNode

        return parent_object

    @property
    def tag_root(self):
        return self.parent_object

    @property
    def here_url(self):
        if hasattr(self, 'original_url') and self.original_url:
            return self.original_url
        else:
            return self.tag_root


    @property
    def available_tags(self):
        try:
            return self.portal_catalog.uniqueValuesFor(self.catalog_index)
        except KeyError:
            return []

    def getFolderContents(self, contentFilter={}):
        tag_root = self.tag_root
        tags = self.tags

        default_page = tag_root.getDefaultPage()

        if tag_root.portal_type == 'Topic':
            return tag_root.queryCatalog(**{self.catalog_index : tags})
        elif default_page in tag_root.objectIds() and tag_root[default_page].portal_type == 'Topic':
            return tag_root[default_page].queryCatalog(**{self.catalog_index : tags})
        elif tags:
            return self.portal_catalog.searchResults({self.catalog_index : tags, 'path' : '/'.join(tag_root.getPhysicalPath())})
        else:
            return []
