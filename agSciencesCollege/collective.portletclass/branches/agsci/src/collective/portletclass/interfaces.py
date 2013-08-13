from zope import schema
from zope.interface import Interface

from . import MessageFactory as _

class ICollectivePortletClassLayer(Interface):
    """Package specific browser layer."""


class ICollectivePortletClass(Interface):
    """Interface with additional CSS class field."""
    collective_portletclass = schema.TextLine(
        title=_(u'portlet-css-class', u'Portlet CSS class'),
        description=_(u'portlet-css-class-description',
            u'Additional CSS class to be set on portlet wrapper.'),
        required=False,
        default=u'',
        )
    mobile_navigation = schema.Bool(
        title=_(u'portlet-mobile-navigation', u'Treat portlet as mobile navigation'),
        description=_(u'portlet-mobile-navigation-description',
            u'If this box is checked, and this portlet is in the left column, it not moved below content.'),
        required=False,
        default=False,
        )