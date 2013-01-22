from agsci.subsite.browser.views.tags import TagsView

class CountyView(TagsView):

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.url_tags = []

        # Overrite configuration
        self.singular_title = 'County'
        self.plural_title = 'Counties'

        self.obj_tags = 'extension_counties'
        self.target_view = 'counties'
        self.catalog_index = 'Counties'

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

    def getFolderContents(self):
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


class ProgramView(CountyView):

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.url_tags = []

        # Overrite configuration
        self.singular_title = 'Course'
        self.plural_title = 'Courses'

        self.obj_tags = 'extension_programs'
        self.target_view = 'courses'
        self.catalog_index = 'Programs'


class TopicView(CountyView):

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.url_tags = []

        # Overrite configuration
        self.singular_title = 'Topic'
        self.plural_title = 'Topics'

        self.obj_tags = 'extension_topics'
        self.target_view = 'topics'
        self.catalog_index = 'Topics'


class SubtopicView(CountyView):

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.url_tags = []

        # Overrite configuration
        self.singular_title = 'Subtopic'
        self.plural_title = 'Subtopics'

        self.obj_tags = 'extension_subtopics'
        self.target_view = 'subtopics'
        self.catalog_index = 'Subtopics'
