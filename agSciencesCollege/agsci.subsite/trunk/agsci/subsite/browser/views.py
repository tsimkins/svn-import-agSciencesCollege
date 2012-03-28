from zope.interface import implements, Interface
from Products.Five import BrowserView
from Products.CMFCore.utils import getToolByName
from Acquisition import aq_acquire, aq_inner, aq_chain
from Products.agCommon.browser.views import FolderView
from agsci.subsite.content.interfaces import IBlog
from plone.memoize.view import memoize

"""
    Interface Definitions
"""

from zope.component import getUtility
from plone.i18n.normalizer.interfaces import IIDNormalizer

class ITagsView(Interface):
    """
    tags view interface
    """

    def test():
        """ test method"""

class TagsView(FolderView):

    implements(ITagsView)

    @property
    def normalizer(self):
        return getUtility(IIDNormalizer)

    def page_title(self):
        tags = []
        for t in self.getTags():
            for rt in self.tags:
                if self.normalizer.normalize(t) == rt:
                    tags.append(t)

        if len(tags) > 1:
            plural = 's'
        else:
            plural = ''
            
        return '%s (Tag%s: %s)' % (self.context_state.object_title(), plural, ', '.join(tags))
    
    def publishTraverse(self, request, name):
        if name:
            self.tags = [name]
        self.original_context = self.context
        self.context = self.getTagRoot()

        return self

    def getTagRoot(self):
        # If we're a Blog object, reset the context to the default page
        if self.context.portal_type == 'Blog':
            default_page_id = self.context.getDefaultPage()
            if default_page_id in self.context.objectIds():
               return self.context[default_page_id]
        return self.context

    @memoize
    def getTags(self):

        try:
            selected_tags = self.tags
        except AttributeError:
            selected_tags = []

        available_tags = {}

        for i in aq_chain(self.context):
            if IBlog.providedBy(i):
                for t in sorted(i.available_public_tags):
                    available_tags[self.normalizer.normalize(t)] = t
                break

        if not available_tags and self.context.portal_type == 'Topic':
            for i in self.context.queryCatalog():
                if i.public_tags:
                    for t in i.public_tags:
                        available_tags[self.normalizer.normalize(t)] = t

        item_tags = []

        for t in selected_tags:
            normal_tag = self.normalizer.normalize(t)
            if available_tags.get(normal_tag):
                item_tags.append(available_tags.get(normal_tag))
                
        return item_tags
        