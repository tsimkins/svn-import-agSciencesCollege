from DateTime import DateTime
from Products.CMFCore.utils import getToolByName
from Products.agCommon.browser.views import FolderView
from plone.i18n.normalizer.interfaces import IIDNormalizer
from zope.component import getUtility
from zope.interface import implements, Interface

class RelatedItemRSSView(FolderView):

    def getFolderContents(self):
        related_item_uids = self.context.getRawRelatedItems()
        if related_item_uids:
            results = self.portal_catalog.searchResults({'UID' : related_item_uids})
            return sorted(results, key=lambda x: related_item_uids.index(x.UID))
        else:
            return []