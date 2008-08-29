from zope.component import getMultiAdapter
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.app.layout.viewlets.common import ViewletBase
from AccessControl import getSecurityManager
from Products.CMFCore.utils import getToolByName


class AdminLinksViewlet(ViewletBase):
    render = ViewPageTemplateFile('templates/adminlinks.pt')
