from Products.agCommon.browser.views import FolderView
from AccessControl import Unauthorized

class CroppableImages(FolderView):

    def allowCrop(self, context):
        try:
            return context.restrictedTraverse('@@crop-image').allowCrop()
        except Unauthorized:
            return False

    def getFolderContents(self, contentFilter={}):
        results = []
        contents = []
        folder_path = ""

        if self.context.portal_type == 'Topic':
            try:
                results = self.context.queryCatalog(**contentFilter)
            except AttributeError:
                # We don't like a relative path here for some reason.
                # Until we figure it out, fall through and just do the default query.
                # That should work in most cases.
                folder_path = '/'.join(self.context.aq_parent.getPhysicalPath())

        if not results:
            catalog = self.portal_catalog

            if not folder_path:
                folder_path = '/'.join(self.context.getPhysicalPath())

            results = self.portal_catalog.searchResults({
                                            'hasContentLeadImage' : True,
                                            'path' : {'query': folder_path,},
                                            'sort_on' : 'effective' })

        for r in results:
            if r.hasContentLeadImage:
                o = r.getObject()
                if self.allowCrop(o):
                    contents.append(r)

        return contents