from zope.app.component.hooks import setSite
from Products.agCommon import calculateGradient
from agsci.w3c.colors import checkColorAccessibility

def checkSiteColorContrast(site):

    setSite(site)
    compliant = True

    custom = site.portal_skins.custom

    if 'base_properties' in custom.objectIds():
        base_properties = custom.base_properties
    elif site.id == 'agsci.psu.edu':
        base_properties = site.portal_skins.agcommon_styles.base_properties
    else:
        return compliant

    # Check button contrast
    e_startColor = base_properties.getProperty('leftButtonBackground_external').replace('#', '')
    e_endColor = calculateGradient(e_startColor)
    e_textColor = base_properties.getProperty('leftButtonTextColor_external').replace('#', '')

    i_startColor = base_properties.getProperty('leftButtonBackground_internal').replace('#', '')
    i_endColor = calculateGradient(i_startColor)
    i_textColor = base_properties.getProperty('leftButtonTextColor_internal').replace('#', '')

    internal_compliant = (checkColorAccessibility(i_textColor, i_startColor) and checkColorAccessibility(i_textColor, i_endColor))
    external_compliant = (checkColorAccessibility(e_textColor, e_startColor) and checkColorAccessibility(e_textColor, e_endColor))

    if not internal_compliant:
        print '%s : internal : %s' % (site.id, str(internal_compliant))
        print "Text: %s, Gstart: %s, Gend: %s\n\n" % (i_textColor, i_startColor, i_endColor)
        compliant = False

    if not external_compliant:
        print '%s : external : %s' % (site.id, str(external_compliant))
        print "Text: %s, Gstart: %s, Gend: %s\n\n" % (e_textColor, e_startColor, e_endColor)
        compliant = False

    # Check front page portlet header contrast
    p_backgroundColor = base_properties.getProperty('frontRightPortletHeaderBackgroundColor').replace('#', '')
    p_textColor = base_properties.getProperty('frontRightPortletHeaderTextColor').replace('#', '')
    front_portlet_header_compliant = checkColorAccessibility(p_textColor, p_backgroundColor)

    if not front_portlet_header_compliant:
        print '%s : front_portlet_header_compliant : %s' % (site.id, str(front_portlet_header_compliant))
        print "Text: %s, Background: %s\n\n" % (p_textColor, p_backgroundColor)
        compliant = False

    # Check top navigation contrast
    t_backgroundColor = base_properties.getProperty('topnavigationBackgroundColor').replace('#', '')
    t_textColor = base_properties.getProperty('topnavigationTextColor').replace('#', '')
    t_textHoverColor = base_properties.getProperty('topnavigationTextHoverColor').replace('#', '')
    t_backgroundActiveColor = base_properties.getProperty('topnavigationAlternateBackgroundColor').replace('#', '')
    t_textActiveColor = base_properties.getProperty('topnavigationAlternateTextColor').replace('#', '')    
    
    topnav_compliant = checkColorAccessibility(t_textColor, t_backgroundColor)
    topnav_hover_compliant = checkColorAccessibility(t_textHoverColor, t_backgroundColor)
    topnav_active_compliant = checkColorAccessibility(t_textActiveColor, t_backgroundActiveColor)
    
    if not topnav_compliant:
        print '%s : topnav_compliant : %s' % (site.id, str(topnav_compliant))
        print "Text: %s, Background: %s\n\n" % (t_textColor, t_backgroundColor)
        compliant = False

    if not topnav_hover_compliant:
        print '%s : topnav_hover_compliant : %s' % (site.id, str(topnav_hover_compliant))
        print "Text: %s, Background: %s\n\n" % (t_textHoverColor, t_backgroundColor)
        compliant = False

    if not topnav_active_compliant:
        print '%s : topnav_active_compliant : %s' % (site.id, str(topnav_active_compliant))
        print "Text: %s, Background: %s\n\n" % (t_textActiveColor, t_backgroundActiveColor)
        compliant = False

    # Check left nav header
    l_backgroundColor = base_properties.getProperty('leftNavTitleBackground').replace('#', '')
    l_textColor = base_properties.getProperty('leftNavTitleColor').replace('#', '')

    leftnav_compliant = checkColorAccessibility(l_textColor, l_backgroundColor)

    if not leftnav_compliant:
        print '%s : leftnav_compliant : %s' % (site.id, str(leftnav_compliant))
        print "Text: %s, Background: %s\n\n" % (l_textColor, l_backgroundColor)
        compliant = False

    return compliant