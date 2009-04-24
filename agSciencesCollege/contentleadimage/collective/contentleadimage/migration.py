from Products.CMFCore.utils import getToolByName
from collective.contentleadimage.interfaces import ILeadImageable
from collective.contentleadimage.config import CONTENT_LEADIMAGE_ANNOTATION_KEY
from collective.contentleadimage.config import IMAGE_FIELD_NAME
from zope.annotation import IAnnotations
import logging
logger = logging.getLogger('leadimgae.migration')


def migrate0xto1(context):
    portal = context.portal_url.getPortalObject()
    ctool  = getToolByName(portal, 'portal_catalog')
    items = ctool(object_provides=ILeadImageable.__identifier__) 
    cnt = len(items)
    logger.info('Migrating %d items' % cnt)
    for item in items:
        obj = item.getObject()
        image = IAnnotations(obj).get(CONTENT_LEADIMAGE_ANNOTATION_KEY, None)
        if image:
            logger.info('Migrating item %s' % '/'.join(obj.getPhysicalPath()))
            field = obj.getField(IMAGE_FIELD_NAME)
            if field and image.get('data', ''):
                field.set(obj, image['data'], mimetype=image['contenttype'])
            # remove annotation key
            del IAnnotations(obj)[CONTENT_LEADIMAGE_ANNOTATION_KEY]