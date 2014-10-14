from PIL import Image, ImageDraw
from Products.CMFCore.utils import getToolByName
from Products.Five import BrowserView
from StringIO import StringIO 
from collective.contentleadimage.utils import getImageAndCaptionFields
from plone.memoize.instance import memoize
from plone.memoize.instance import memoize
from zope.component import getUtility
from zope.interface import implements
from zope.publisher.interfaces import IPublishTraverse
import base64

class CropImageView(BrowserView):

    implements(IPublishTraverse)

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.path = []

    def publishTraverse(self, request, name):
        self.path.append(name)
        return self

    def imageDimensions(self):
        if self.image:
            return (self.image.width, self.image.height)
        else:
            return (0,0)

    def imageOrientation(self):
        
        (w,h) = self.imageDimensions()
        
        if w > h:
            return 'landscape'
        elif h > w:
            return 'portrait'
        else:
            return 'square'

    def newImageDimensions(self):

        dimensions = (w,h) = self.imageDimensions()

        image_orientation = self.imageOrientation()
        
        if image_orientation == 'landscape':
            ratio = 3.0/2.0
        elif image_orientation == 'portrait':
            ratio = 3.0/4.0
        else: #square
            return (w,h)

        new_h = w/ratio
        new_w = h*ratio

        if new_w < w:
            dimensions = (new_w, h)
        else:
            dimensions = (w, new_h)

        return tuple([int(round(x)) for x in dimensions])

    @property
    def crop_base(self):
        for i in ['left', 'right', 'top', 'bottom']:
            if i in self.path:
                return i
        return None

    @property
    def preview(self):
        return 'preview' in self.path

    @property
    def commit(self):
        return 'commit' in self.path

    @property
    def image(self):
        return self.getOriginalImage()

    def getCropCoords(self):

        (w1,h1) = self.imageDimensions()
        (w2,h2) = self.newImageDimensions()

        w_diff = (w1 - w2)
        h_diff = (h1 - h2)

        (x0, y0, x1, y1) = (
            w_diff/2.0,
            h_diff/2.0,
            w1 - w_diff/2.0,
            h1 - h_diff/2.0
        )
        
        if self.crop_base == 'left':
            x0 = 0
            x1 = w2
        elif self.crop_base == 'right':
            x0 = w_diff
            x1 = w_diff + w2
        elif self.crop_base == 'top':
            y0 = 0
            y1 = h2
        elif self.crop_base == 'bottom':
            y0 = h_diff
            y1 = h_diff + h2
        
        coords = (x0, y0, x1, y1)

        return tuple([int(round(x)) for x in coords])

    def getFormat(self):
        type = self.getContentType()
        return {
            'image/jpeg' : 'JPEG',
            'image/png' : 'PNG',
            'image/gif' : 'GIF',
        }.get(type, 'UNK')

    def topUrl(self):
        return '%s/@@%s/top' % (self.context.absolute_url(), self.__name__)

    def bottomUrl(self):
        return '%s/@@%s/bottom' % (self.context.absolute_url(), self.__name__)

    def leftUrl(self):
        return '%s/@@%s/left' % (self.context.absolute_url(), self.__name__)

    def rightUrl(self):
        return '%s/@@%s/right' % (self.context.absolute_url(), self.__name__)

    def middleUrl(self):
        return '%s/@@%s/middle' % (self.context.absolute_url(), self.__name__)

    def previewUrl(self):
        return '%s/@@%s/%s/preview' % (self.context.absolute_url(), self.__name__, self.crop_base)

    def commitUrl(self):
        return '%s/@@%s/%s/commit' % (self.context.absolute_url(), self.__name__, self.crop_base)

    def imageTallOrWide(self):
        (w1,h1) = self.imageDimensions()
        (w2,h2) = self.newImageDimensions()

        if w1 > w2:
            return 'wide'
        elif h1 > h2:
            return 'tall'
        else:
            return None

    def imageTall(self):
        return (self.imageTallOrWide() == 'tall')

    def imageWide(self):
        return (self.imageTallOrWide() == 'wide')

    def getContentType(self):
        if self.image:
            return self.image.getContentType()
        else:
            return ''

    def image_base64(self):
        content_type = self.getContentType()
        cropped_image_data = self.getCroppedImage()
        b64_image_data = base64.b64encode(cropped_image_data)
        uri = "data:%s;base64,%s" % (content_type, b64_image_data)
        return uri

    @memoize
    def getOriginalImage(self):
        image_field = self.getImageField()
        
        if image_field:

            image = image_field.get(self.context)
            
            if image:
                if hasattr(image, 'size') and image.size:
                    return image
                elif hasattr(image, 'get_size') and image.get_size():
                    return image
        
        return ''

    def getImageField(self):
        (image_field, imagecaption_field) = getImageAndCaptionFields(self.context)
        return image_field

    def allowCrop(self):

        mt = getToolByName(self.context, 'portal_membership')
        member = mt.getAuthenticatedMember()

        if not member.has_role('Manager', self.context):
            return False

        old_dimensions = self.imageDimensions()
        new_dimensions = self.newImageDimensions()

        return (new_dimensions != old_dimensions)


    def getCroppedImage(self):

        image = self.image        
        
        if image and self.allowCrop():
    
            (x0,y0,x1,y1) = new_coords = self.getCropCoords()
            
            x1 = x1 - 1
            y1 = y1 - 1
                        
            try:
                raw = image.data.data
            except AttributeError:
                raw = image.data

            pil_image = Image.open(StringIO(raw))

            if self.preview or self.commit:
                pil_image = pil_image.crop(new_coords)
            else:
                preview = ImageDraw.Draw(pil_image)
                preview.line([(x0,y0), (x1,y0)], fill="#FF8A00", width=3)
                preview.line([(x1,y0), (x1,y1)], fill="#FF8A00", width=3)
                preview.line([(x1,y1), (x0,y1)], fill="#FF8A00", width=3)
                preview.line([(x0,y0), (x0,y1)], fill="#FF8A00", width=3)

            img_buffer = StringIO()    
            content_type = self.getContentType()
            pil_image.save(img_buffer, self.getFormat(), quality=90)

            img_value = img_buffer.getvalue()

            if self.commit:
                # Update image
                image_field = self.getImageField()
                image_field.set(self.context, img_value)
                image_field.removeScales(self.context)
                image_field.createScales(self.context)
                return self.request.RESPONSE.redirect(self.context.absolute_url())

            return img_value

        return ''