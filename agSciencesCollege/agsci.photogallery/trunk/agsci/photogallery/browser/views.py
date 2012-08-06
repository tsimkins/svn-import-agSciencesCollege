from zope.interface import implements, Interface
from Products.Five import BrowserView
from Products.CMFCore.utils import getToolByName
from Products.ATContentTypes.interface import IATTopic
from zope.component import getUtility, getMultiAdapter
from agsci.photogallery.browser.interfaces import *
from zope.component import getUtility


"""
    Interface Definitions
"""

class PhotoGalleryView(BrowserView):

    implements(IPhotoGalleryView)

    def __init__(self, context, request):
        self.context = context
        self.request = request
        
    def getImages(self):
        if IATTopic.providedBy(self.context):
            # ATTopic like content
            # Call Products.ATContentTypes.content.topic.ATTopic.queryCatalog() method
            # This method handles b_start internally and
            # grabs it from HTTPRequest object
            return self.context.queryCatalog(contentFilter={'portal_type' : 'Image'}, batch=False, b_size=100)

        else:
            # Folder or Large Folder like content
            # Call CMFPlone(/skins/plone_scripts/getFolderContents Python script
            # This method handles b_start parametr internally and grabs it from the request object
            return self.context.getFolderContents(contentFilter={'portal_type' : 'Image'}, batch=False, b_size=100)

