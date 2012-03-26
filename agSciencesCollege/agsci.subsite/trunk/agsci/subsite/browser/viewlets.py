from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.app.layout.viewlets.common import ViewletBase
from zope.component import getMultiAdapter
           
class TagsViewlet(ViewletBase):
    
    index = ViewPageTemplateFile('templates/tags_viewlet.pt')

    def update(self):
        context_state = getMultiAdapter((self.context, self.request),
                                        name=u'plone_context_state')
    @property
    def portal_state(self):
        return getMultiAdapter((self.context, self.request),
                                name=u'plone_portal_state')

    @property
    def anonymous(self):
        return self.portal_state.anonymous()
