from zope.interface import implements, Interface
from Products.Five import BrowserView
from Products.CMFCore.utils import getToolByName
from Acquisition import aq_acquire, aq_inner, aq_chain
from Products.agCommon.browser.views import FolderView
from agsci.subsite.content.interfaces import IBlog

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
    
    def publishTraverse(self, request, name):
        if name:
            self.tags = [name]
        import pdb; pdb.set_trace()
        return self

    def getTags(self):

        try:
            selected_tags = self.tags
        except AttributeError:
            selected_tags = []

        available_tags = {}

        normalizer = getUtility(IIDNormalizer)

        for i in aq_chain(self.context):
            if IBlog.providedBy(i):
                for t in sorted(i.available_public_tags):
                    available_tags[normalizer.normalize(t)] = t
                break

        item_tags = []

        for t in selected_tags:
            normal_tag = normalizer.normalize(t)
            if available_tags.get(normal_tag):
                item_tags.append(available_tags.get(normal_tag))
        return item_tags
        