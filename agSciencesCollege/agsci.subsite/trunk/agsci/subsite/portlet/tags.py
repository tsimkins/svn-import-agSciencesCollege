from zope import schema
from zope.component import getMultiAdapter
from zope.formlib import form
from zope.interface import implements
from plone.memoize.compress import xhtml_compress

from plone.app.portlets.portlets import base
from plone.memoize.instance import memoize
from plone.portlets.interfaces import IPortletDataProvider
from plone.app.portlets.cache import render_cachekey

from Acquisition import aq_chain
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFPlone import PloneMessageFactory as _
from Products.CMFCore.utils import getToolByName
from Products.CMFCore.interfaces import IFolderish
from Products.CMFPlone.interfaces import IPloneSiteRoot

from agsci.subsite.content.interfaces import ITagRoot

from zope.component import getUtility
from plone.i18n.normalizer.interfaces import IIDNormalizer

class ITag(IPortletDataProvider):

    header = schema.TextLine(
        title=_(u"Portlet header"),
        description=_(u"Title of the rendered portlet"),
        required=True)

    show_header = schema.Bool(
        title=_(u"Show portlet header"),
        description=_(u""),
        required=True,
        default=False)

    hide = schema.Bool(
        title=_(u"Hide portlet"),
        description=_(u"Tick this box if you want to temporarily hide "
                      "the portlet without losing your text."),
        required=True,
        default=False)

class Assignment(base.Assignment):

    implements(ITag)

    header = ""
    show_header = False
    hide = False

    def __init__(self, header=u"", show_header=False, hide=False, *args, **kwargs):
        base.Assignment.__init__(self, *args, **kwargs)
        self.header = header
        self.show_header = show_header
        self.hide = hide
                
    @property
    def title(self):
        if self.header:
            return self.header
        else:
            return "Tags"


class Renderer(base.Renderer):
    _template = ViewPageTemplateFile('templates/tags.pt')

    def __init__(self, *args):
        base.Renderer.__init__(self, *args)
        
        # Defines the data and view fields for this portlet.  Used so we can 
        # subclass the portlet.
        self.tag_listing = 'available_public_tags'
        self.obj_tags = 'public_tags'
        self.target_view = 'tags'
        self.catalog_index = 'Tags'

    @property
    def portal_catalog(self):
        return getToolByName(self.context, 'portal_catalog')
        
    @property
    def parent_object(self):
       
        # parent_object is the portlet's parent
        # Default to self.context
        parent_object = self.context
        
        # If context is the default page, set parent_object to parentNode
        parentNode = self.context.getParentNode()
        
        if hasattr(parentNode, 'getDefaultPage') and parentNode.getDefaultPage() == self.context.getId():
            parent_object = parentNode

        # Finally, all this goes out the window if we're inside a object that
        # implements ITagRoot (for example, a blog)

        for i in aq_chain(self.context):
            if ITagRoot.providedBy(i):
                parent_object = i
                break

        return parent_object

    @property
    def available_tags(self):

        available_tags = []

        tag_root = self.tag_root
        
        if hasattr(tag_root, self.tag_listing):
            available_tags = getattr(tag_root, self.tag_listing)        

        if not available_tags:
            available_tags = self.portal_catalog.uniqueValuesFor(self.catalog_index)

        return available_tags

    @property
    def tag_root(self):

        for i in aq_chain(self.context):
            if IPloneSiteRoot.providedBy(i):
                return i
            if ITagRoot.providedBy(i):
                return i

        # Probably not needed, but just so we return something.
        return context

    @property
    def tags(self):
        normalizer = getUtility(IIDNormalizer)
        tag_root = self.tag_root
        
        available_tags = self.available_tags
        tags = {}
        normalized_tags = []

        if self.context.portal_type == 'Topic':
            items = self.context.queryCatalog()
        else:                
            path = '/'.join(tag_root.getPhysicalPath())
            items = self.portal_catalog.searchResults({self.catalog_index : available_tags, 'path' : path})                

        for i in items:
            if hasattr(i, self.obj_tags):
                obj_tags = getattr(i, self.obj_tags)

                if not obj_tags:
                    obj_tags = []
                    
                for t in obj_tags:
                    if available_tags:
                        if t in available_tags:
                            tags[t] = 1
                    else:
                        tags[t] = 1
       
        for t in sorted(tags.keys()):
            normalized_tags.append([normalizer.normalize(t), t])    

        return normalized_tags

    def render(self):
        return xhtml_compress(self._template())

    @property
    def available(self):
        return self.tags and not self.data.hide


class AddForm(base.AddForm):
    form_fields = form.Fields(ITag)
    label = _(u"Add Tag Portlet")
    description = _(u"This portlet displays tag information.")

    def create(self, data):
        return Assignment(**data)

class EditForm(base.EditForm):
    form_fields = form.Fields(ITag)
    label = _(u"Edit Tag Portlet")
    description = _(u"This portlet displays tag information.")
