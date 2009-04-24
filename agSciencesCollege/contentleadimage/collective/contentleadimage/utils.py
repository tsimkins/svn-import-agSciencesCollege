from Products.CMFPlone.CatalogTool import registerIndexableAttribute
from collective.contentleadimage.interfaces import ILeadImageable
from collective.contentleadimage.config import IMAGE_FIELD_NAME

def hasContentLeadImage(obj, portal, **kw):
    if ILeadImageable.providedBy(obj):
        field = obj.getField(IMAGE_FIELD_NAME)
        if field is not None:
            value = field.get(obj)
            return not not value
    return False

registerIndexableAttribute('hasContentLeadImage', hasContentLeadImage)
