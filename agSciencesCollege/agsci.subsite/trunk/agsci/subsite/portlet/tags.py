from zope import schema
from zope.component import getMultiAdapter
from zope.formlib import form
from zope.interface import implements
from plone.memoize.compress import xhtml_compress

from plone.app.portlets.portlets import base
from plone.memoize.instance import memoize
from plone.portlets.interfaces import IPortletDataProvider
from plone.app.portlets.cache import render_cachekey

from Acquisition import aq_acquire, aq_inner, aq_chain
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFPlone import PloneMessageFactory as _
from Products.CMFCore.utils import getToolByName
from Products.CMFCore.interfaces import IFolderish

from agsci.subsite.content.interfaces import IBlog

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

    def __init__(self, header=u"", show_header=False, hide=False):
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

        context = aq_inner(self.context)
        
        # parent_object is the portlet's parent
        # Default to self.context
        self.parent_object = context
        
        # If context is the default page, set parent_object to parentNode
        parentNode = context.getParentNode()
        
        if parentNode.getDefaultPage() == self.context.getId():
            self.parent_object = parentNode
        
        # Finally, all this goes out the window if we're inside a blog.  Blog
        # is the parent object.
        for i in aq_chain(context):
            if IBlog.providedBy(i):
                self.parent_object = i
                break
                
        portal_state = getMultiAdapter((context, self.request), name=u'plone_portal_state')
        self.anonymous = portal_state.anonymous()
        self.portal_url = portal_state.portal_url()
        self.typesToShow = portal_state.friendly_types()

        plone_tools = getMultiAdapter((context, self.request), name=u'plone_tools')
        self.catalog = plone_tools.catalog()
        
        context_state = getMultiAdapter((self.context, self.request), name=u'plone_context_state')

        self.tags = self.getTags()

    def getTags(self):
        normalizer = getUtility(IIDNormalizer)
        context = aq_inner(self.context)

        tags = {}
        path = ""
        available_tags = []
        normalized_tags = []
        
        for i in aq_chain(context):
            if IBlog.providedBy(i):
                path = "/".join(i.getPhysicalPath())
                available_tags = i.available_public_tags
                break

        if self.context.portal_type == 'Topic':
            items = self.context.queryCatalog()
        else:                
            if not path:
                if not IFolderish.providedBy(i):
                    path = '/'.join(self.context.getPhysicalPath()[0:-1])
                else:
                    path = '/'.join(self.context.getPhysicalPath())
                    
            if not available_tags:
                available_tags = self.catalog.uniqueValuesFor('Tags')

            items = self.catalog.searchResults({'Tags' : available_tags, 'path' : path})                
            

        for i in items:
            if i.public_tags:
                for t in i.public_tags:
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
    description = _(u"This portlet displays tag information for everything in the blog.")

    def create(self, data):
        return Assignment(**data)

class EditForm(base.EditForm):
    form_fields = form.Fields(ITag)
    label = _(u"Edit Tag Portlet")
    description = _(u"This portlet displays tag information for everything in the blog.")
