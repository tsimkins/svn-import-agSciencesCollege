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
        if collective_portletclass:
            klasses.extend(collective_portletclass.split())
        if mobile_navigation:
            klasses.append("mobile-navigation")
        if klasses:
            return ' ' + " ".join(["portlet-%s" % x for x in klasses])
        else:
            return ""