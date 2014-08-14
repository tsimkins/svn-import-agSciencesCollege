# CSS Template variables

from zope.app.component.hooks import getSite
from Products.CMFCore.utils import getToolByName
import re

# Properties

tile_homepage_padding = 15.0

def total_width():
    return 899.0
    default_width = 1000.0
    site = getSite()
    try:
        portal_skins = getToolByName(site, 'portal_skins')
    except AttributeError:
        return default_width

    try:
        base_properties = portal_skins.restrictedTraverse('agcommon_styles/base_properties')
    except KeyError:
        return default_width

    width = base_properties.getProperty('maxWidth', '')

    if not width:
        return default_width

    width = re.sub('[A-Za-z]+', '', width)

    try:
        return float(width)
    except ValueError:
        return default_width


# Tile Homepage CSS templates

portlet_rss_image = """

#content #portlets-above .portlet-width-%(block_klass)s.portlet-item-count-1 .rssImage {
    width: 33%%;
    float: right;
    margin: 0 0 0.125em 0.25em;
    padding: 0;
}
"""

portlet_block_css = """
        
#content #portlets-above .portlet-width-%(block_klass)s {
    width: %(block_percent)0.6f%%;
    float: left;
    padding: 0;
    margin: 0.5em 0;
}

#content #portlets-above .portlet-width-%(block_klass)s .portletHeader,
#content #portlets-above .portlet-width-%(block_klass)s .portletFooter,
#content #portlets-above .portlet-width-%(block_klass)s img.feedmixerCollectionLeadImage {
    width: %(content_width_percent)0.6f%%;
    margin-left: %(content_margin_percent)0.6f%%;
    margin-right: %(content_margin_percent)0.6f%%;    
    display: block;
}

#content #portlets-above .portlet-width-%(block_klass)s .portletFooter {
    clear: both;
}

#content #portlets-above .portlet-width-%(block_klass)s img.feedmixerCollectionLeadImage {
    padding: 0;
    height: auto;
}

"""

portlet_item_css = """

#content #portlets-above .portlet-width-%(block_klass)s.portlet-item-count-%(n)s .portletItem {
    width: %(content_width_percent)0.6f%%;
    margin-left: %(padding_percent)0.6f%%;
    margin-right: %(padding_percent)0.6f%%;
    float: left;
}

#content #portlets-above .portlet-width-%(block_klass)s.portlet-item-count-%(n)s .portletItem:nth-child(%(n_child)sn + 1) {
    clear: left;
}
"""

contentwellportlet_css = """
#content #portlets-above {
    display: block;
}

div.AbovePortletManager1, 
div.AbovePortletManager2, 
div.AbovePortletManager3, 
div.AbovePortletManager4, 
div.AbovePortletManager5 {
    float: none;
    clear: both;
    width: 100%%;
    margin: 0;
    padding: 0;
}

"""

portlet_css = """
#content #portlets-above .portlet {
    margin-bottom: 1em;
}

#content #portlets-above .portlet img {
    max-width: 100%;
    width: 100%;
    height: auto;
}

#content #portlets-above .rssImage {
    margin-bottom: 0.25em;
}

"""
