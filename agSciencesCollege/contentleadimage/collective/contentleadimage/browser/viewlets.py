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

    def bodyTag(self, css_class=''):
        """ returns img tag """
        context = aq_inner(self.context)
        
        # Use News Item image as Content Lead Image, if it exists
        field = None
        
        leadimagefield = context.getField(IMAGE_FIELD_NAME)
        newsitemfield =  context.getField('image')

        if leadimagefield:
            field = leadimagefield
        if newsitemfield:
            field = newsitemfield
        
        if field is not None:
            if field.get_size(context) != 0:
                scale = self.prefs.body_scale_name
                return field.tag(context, scale=scale, css_class=css_class)
        return ''

    def descTag(self, css_class='tileImage'):
        """ returns img tag """
        context = aq_inner(self.context)

        # Use News Item image as Content Lead Image image, if it exists
        field = None
        
        leadimagefield = context.getField(IMAGE_FIELD_NAME)
        newsitemfield =  context.getField('image')

        if leadimagefield:
            field = leadimagefield
        if newsitemfield:
            field = newsitemfield
            
        if field is not None:
            if field.get_size(context) != 0:
                scale = self.prefs.desc_scale_name
                return field.tag(context, scale=scale, css_class=css_class)
        return ''

    def caption(self):
        context = aq_inner(self.context)
        
        # Use News Item caption as Content Lead Image caption, if it exists
        if context.getField(IMAGE_FIELD_NAME):
            return context.widget(IMAGE_CAPTION_FIELD_NAME, mode='view')
        elif context.getField('imageCaption'):
            return context.widget('imageCaption', mode='view')
        else:
            return ''
        
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
