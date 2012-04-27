from Acquisition import aq_inner, aq_acquire
from zope.component import getUtility, getMultiAdapter
from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFPlone.interfaces import IPloneSiteRoot
from collective.contentleadimage.config import IMAGE_FIELD_NAME
from collective.contentleadimage.config import IMAGE_CAPTION_FIELD_NAME
from collective.contentleadimage.leadimageprefs import ILeadImagePrefsForm

class FolderLeadImageView(BrowserView):
    
    template = ViewPageTemplateFile('folder_leadimage_view.pt')

    @property
    def prefs(self):
        portal = getUtility(IPloneSiteRoot)
        return ILeadImagePrefsForm(portal)

    def tag(self, obj, css_class='tileImage'):
        context = aq_inner(obj)
        field = context.getField(IMAGE_FIELD_NAME)
        titlef = context.getField(IMAGE_CAPTION_FIELD_NAME)
        if titlef is not None:
            title = titlef.get(context)
        else:
            title = ''
        if field is not None:
            if field.get_size(context) != 0:
                scale = self.prefs.desc_scale_name
                return field.tag(context, scale=scale, css_class=css_class, title=title)
        return ''

    def __init__(self, context, request):
        BrowserView.__init__(self, context, request)
        self.update()
        
    def __call__(self):
        return self.template()
        
    def update(self):
        context_state = getMultiAdapter((self.context, self.request),
                                        name=u'plone_context_state')
                                        
        try:
            show_date = aq_acquire(self.context, 'show_date')
        except AttributeError:
            show_date = False
        
        self.show_date = show_date
