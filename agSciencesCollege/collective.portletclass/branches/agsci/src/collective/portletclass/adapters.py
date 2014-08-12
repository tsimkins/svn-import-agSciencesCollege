from zope.component import adapts
from plone.app.portlets.manager import ColumnPortletManagerRenderer, DashboardPortletManagerRenderer
from zope.interface import Interface
from zope.publisher.interfaces.browser import IBrowserView
from zope.publisher.interfaces.browser import IDefaultBrowserLayer
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.app.portlets.interfaces import IColumn
from plone.app.portlets.interfaces import IDashboard
from collective.portletclass.interfaces import ICollectivePortletClassLayer
from Products.ContentWellPortlets.browser.manager import ContentWellPortletRenderer

class CustomColumnPortletManagerRenderer(ColumnPortletManagerRenderer):
    template = ViewPageTemplateFile('templates/column.pt')


class CustomDashboardPortletManagerRenderer(DashboardPortletManagerRenderer):
    template = ViewPageTemplateFile('templates/dashboard-column.pt')


class CustomContentWellPortletRenderer(ContentWellPortletRenderer):
    template = ViewPageTemplateFile('templates/contentwellportlets.pt')
