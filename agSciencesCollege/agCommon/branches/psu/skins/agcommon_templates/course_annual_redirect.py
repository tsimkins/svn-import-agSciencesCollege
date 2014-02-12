##title=Annual Course Redirect

"""
course_annual_redirect
Redirect to the course's upcoming event if, and only if:
 - The course collection has a 'course-annual' tag
 - There is one and only one upcoming event
 - AND current user is logged out
"""

from Products.CMFCore.utils import getToolByName
from zope.component import getMultiAdapter

request = container.REQUEST
RESPONSE =  request.RESPONSE

portal_state = getMultiAdapter((context, request), name=u'plone_portal_state')
anonymous = portal_state.anonymous()

results = context.queryCatalog()

if results and len(results) == 1 and anonymous:
    event = results[0]
    return RESPONSE.redirect(event.getURL())
else:
    if not anonymous:
        RESPONSE.setHeader('Cache-Control', 'max-age=0, must-revalidate, private')
    else:
        RESPONSE.setHeader('Cache-Control', 'max-age=0, s-maxage=300, must-revalidate, public, proxy-revalidate')

    return context.atct_topic_view()
