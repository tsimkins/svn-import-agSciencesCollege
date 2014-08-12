from zope import schema
from zope.interface import Interface
from . import MessageFactory as _

from zope.schema import vocabulary

def portlet_width_vocab():

    vocab = []    

    widths = []

    for i in range(1,6):
        for j in range(1,i+1):
            widths.append(((100.0*j)/i))
    
    widths = [int(x) for x in sorted(list(set(widths)))]
    
    for i in widths:
        vocab.append( vocabulary.SimpleVocabulary.createTerm(i, '%d' % i, '%d%%' % i) )

    return vocabulary.SimpleVocabulary(vocab)

def portlet_item_count_vocab():

    vocab = []    

    widths = []

    for i in range(1,6):

        vocab.append( vocabulary.SimpleVocabulary.createTerm(i, '%d' % i, '%d' % i) )

    return vocabulary.SimpleVocabulary(vocab)


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
    parent_only = schema.Bool(
        title=_(u'portlet-parent-only', u'Only show portlet on this object.'),
        description=_(u'portlet-parent-only-description',
            u'Overrides portlet display for child objects.'),
        required=False,
        default=False,
        )
    more_text = schema.Bool(
        title=_(u'portlet-more-text', u'Show portlet title in "More" text.'),
        description=_(u'portlet-more-text-description',
            u'For Feedburner and Collection portlets'),
        required=False,
        default=False,
        )
    more_text_custom = schema.TextLine(
        title=_(u'portlet-more-text-custom', u'Custom "More" text'),
        description=_(u'portlet-more-text-custom-description',
            u'Do not include "More" for this field.'),
        required=False,
        default=u'',
        )
    portlet_width = schema.Choice(
        title=_(u'portlet-width', u'Portlet Percent Width'),
        description=_(u'portlet-width-description', u'Ensure all portlets for the manager add up to 100%.'),
        required=True,
        vocabulary=portlet_width_vocab(),
        default=100,
        )
    portlet_item_count = schema.Choice(
        title=_(u'portlet-item-width', u'Portlet Item count'),
        description=_(u'portlet-width-description', u'Number of items in row for portlet'),
        required=True,
        vocabulary=portlet_item_count_vocab(),
        default=1,
        )
