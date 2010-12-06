from collective.contentleadimage.interfaces import ILeadImageable
from collective.contentleadimage.config import IMAGE_FIELD_NAME

# try:
#     from plone.indexer import indexer
#     from zope.component import provideAdapter
#     HAS_INDEXER = True
# except ImportError:
#     from Products.CMFPlone.CatalogTool import registerIndexableAttribute
#     HAS_INDEXER = False
# 
# if HAS_INDEXER:
#     @indexer(ILeadImageable)
#     def hasContentLeadImage(obj):
#         field = obj.getField(IMAGE_FIELD_NAME)
#         if field is not None:
#             value = field.get(obj)
#             return not not value
#     provideAdapter(hasContentLeadImage, name='hasContentLeadImage')
#     
# else:

from Products.CMFPlone.CatalogTool import registerIndexableAttribute
def hasContentLeadImage(obj, portal, **kw):
    if ILeadImageable.providedBy(obj):
        field = obj.getField(IMAGE_FIELD_NAME)
        if field is not None:
            value = field.get(obj)
            return not not value
    return False
registerIndexableAttribute('hasContentLeadImage', hasContentLeadImage)
