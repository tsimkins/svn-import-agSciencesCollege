from Acquisition import aq_inner
from zope.component import getUtility
from zope.component import getMultiAdapter
from plone.app.layout.viewlets import ViewletBase
from Products.CMFPlone.interfaces import IPloneSiteRoot
from collective.contentleadimage.config import IMAGE_FIELD_NAME
from collective.contentleadimage.config import IMAGE_CAPTION_FIELD_NAME
from collective.contentleadimage.leadimageprefs import ILeadImagePrefsForm

# We're going to display the lead image first, and then the news item image.
# This gets the news item image out of the body and into the content lead image viewlet
# for standardization purposes.

class LeadImageViewlet(ViewletBase):
    """ A simple viewlet which renders leadimage """

    @property
    def prefs(self):
        portal = getUtility(IPloneSiteRoot)
        return ILeadImagePrefsForm(portal)

    @property
    def full_width(self):

        full_width = False

        context = aq_inner(self.context)

        full_widthfield = context.getField('leadimage_full_width')

        if full_widthfield:
            full_width = full_widthfield.get(context)

        return full_width

    def getImageAndCaptionFields(self):

        context = aq_inner(self.context)

        # Use News Item image as Content Lead Image, if it exists
        
        leadimagefield = context.getField(IMAGE_FIELD_NAME)
        newsitemfield =  context.getField('image')
        
        leadimagecaption = context.getField(IMAGE_CAPTION_FIELD_NAME)
        newsitemcaption = context.getField('imageCaption')
        
        if leadimagefield and leadimagecaption:
            return (leadimagefield, leadimagecaption)

        elif newsitemfield and newsitemcaption:
            return (newsitemfield, newsitemcaption)

        else:
            return (None, None)

    def bodyTag(self, css_class=''):
        """ returns img tag """

        context = aq_inner(self.context)

        (imageField, imageCaptionField) = self.getImageAndCaptionFields()

        imageCaption = None

        if imageCaptionField:
            imageCaption = str(imageCaptionField.get(context)).strip()
        
        if not imageCaption:
            imageCaption = context.Title()


        if imageField is not None and \
           imageField.getFilename(context) is not None and \
           imageField.get_size(context) != 0:

                if self.full_width:
                    scale = "galleryzoom"
                else:
                    scale = self.prefs.body_scale_name
                
                return imageField.tag(context, scale=scale, css_class=css_class,alt=imageCaption,title=imageCaption)

        return ''

    def caption(self):
        context = aq_inner(self.context)

        (imageField, imageCaptionField) = self.getImageAndCaptionFields()

        imageCaption = ''

        if imageCaptionField:
            imageCaption = str(imageCaptionField.get(context)).strip()

        return imageCaption

    def render(self):
        context = aq_inner(self.context)
        portal_type = getattr(context, 'portal_type', None)
        
        # Special case for News Item
        if portal_type in self.prefs.allowed_types or portal_type == 'News Item':
            return super(LeadImageViewlet, self).render()
        else:
            return ''

    # Used in page template to determine if we're working with a news item
    def isNewsItem(self):
        context = aq_inner(self.context)
        portal_type = getattr(context, 'portal_type', None)
        return portal_type == 'News Item'

    def getClass(self):

        if self.full_width:
            (imageField, imageCaptionField) = self.getImageAndCaptionFields()
            
            if imageField:
                img = imageField.get(self.context)
                if img:
                    width = img.width
                    # Don't stretch the image if it isn't full-width
                    if width < 650: # Magic number! 
                        return "contentLeadImageContainerLeft"
            
            return "contentLeadImageContainerFullWidth"
        else:
            return "contentLeadImageContainer"
