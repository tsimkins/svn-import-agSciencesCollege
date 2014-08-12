from zope.i18nmessageid import MessageFactory
from zope.interface import implements, Interface
from Products.Five import BrowserView

MessageFactory = MessageFactory('collective.portletclass')

class ICollectivePortletClassUtilities(Interface):

    def getPortletClass(self):
        pass

class CollectivePortletClassUtilities(BrowserView):

    implements(ICollectivePortletClassUtilities)

    def getPortletClass(self, assignment):
        klasses = []
        collective_portletclass = getattr(assignment, 'collective_portletclass', '')
        mobile_navigation = getattr(assignment, 'mobile_navigation', False)
        portlet_width = getattr(assignment, 'portlet_width', '')
        portlet_item_count = getattr(assignment, 'portlet_item_count', '')
        if collective_portletclass:
            klasses.extend(collective_portletclass.split())
        if mobile_navigation:
            klasses.append("mobile-navigation")
        if portlet_width:
            klasses.append('width-%s' % portlet_width)
        if portlet_item_count:
            klasses.append('item-count-%s' % portlet_item_count)
        if klasses:
            return ' ' + " ".join(["portlet-%s" % x for x in klasses])
        else:
            return ""