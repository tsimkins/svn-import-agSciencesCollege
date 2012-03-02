from plone.app.layout.viewlets.common import ViewletBase
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.component import getMultiAdapter

class HappyFaceViewlet(ViewletBase):

    index = ViewPageTemplateFile('templates/happyface.pt')

    def update(self):
        context_state = getMultiAdapter((self.context, self.request),
                                        name=u'plone_context_state')
        self.site_actions = context_state.actions('site_actions')


    def isHappy(self):
        return 'z' in self.context.Title().lower()
