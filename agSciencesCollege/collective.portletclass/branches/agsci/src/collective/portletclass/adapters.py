from zope.component import adapts
from plone.app.portlets.manager import ColumnPortletManagerRenderer, DashboardPortletManagerRenderer
from zope.interface import Interface
from zope.publisher.interfaces.browser import IBrowserView
from zope.publisher.interfaces.browser import IDefaultBrowserLayer
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.app.portlets.interfaces import IColumn
from plone.app.portlets.interfaces import IDashboard
from collective.portletclass.interfaces import ICollectivePortletClassLayer

class CustomColumnPortletManagerRenderer(ColumnPortletManagerRenderer):
    adapts(Interface, IDefaultBrowserLayer, IBrowserView, IColumn, ICollectivePortletClassLayer)
    template = ViewPageTemplateFile('templates/column.pt')


class CustomDashboardPortletManagerRenderer(DashboardPortletManagerRenderer):
    adapts(Interface, IDefaultBrowserLayer, IBrowserView, IColumn, ICollectivePortletClassLayer)
    template = ViewPageTemplateFile('templates/dashboard-column.pt')