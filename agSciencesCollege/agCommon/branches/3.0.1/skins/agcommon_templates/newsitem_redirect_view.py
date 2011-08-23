##title=News Item Redirect View

"""
newsitem_redirect_view
Redirect to the News Item's website target URL, if and only if:
 - A website entry exists
 - AND current user doesn't have permission to edit the News Item
"""

from Products.CMFCore.utils import getToolByName

mtool = getToolByName(context, 'portal_membership')

can_edit = mtool.checkPermission('Modify portal content', context)

try:
    redirectURL = context.article_link
except AttributeError:
    redirectURL = None

if redirectURL and not can_edit:
    # Send to the configured website
    return context.REQUEST.RESPONSE.redirect(redirectURL)
else:
    # newsitem_view.pt is a template in the plone_content skin layer
    request = container.REQUEST
    RESPONSE =  request.RESPONSE
    RESPONSE.setHeader('Cache-Control', 'max-age=0, s-maxage=86400, must-revalidate, public, must-revalidate, proxy-revalidate')
    return context.newsitem_view()
