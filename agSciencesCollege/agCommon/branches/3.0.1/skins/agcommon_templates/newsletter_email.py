##title=Newsletter Email View

"""
newsletter_email_view
 - Post-processing on newsletter for email
"""

from Products.CMFCore.utils import getToolByName

import premailer

mtool = getToolByName(context, 'portal_membership')

can_edit = mtool.checkPermission('Modify portal content', context)

html = premailer.transform(context.newsletter_view())

tags = ['dl', 'dt', 'dd']

for tag in tags:
    html = html.replace("<%s" % tag, "<div")
    html = html.replace("</%s" % tag, "</div")
    
return html
