request = container.REQUEST

from Products.CMFCore.utils import getToolByName
portal_catalog = getToolByName(context, "portal_catalog")

event_info = { 'event-name' : None,
               'event-description' : None, 
               'event-date' : None, 
               'event-organizer-email' : None,
               'more-information' : None,
               'contact-name' : None,
               'contact-email' : None,
               'contact-phone' : None,
              }


uid = request.form.get('uid', None)

if uid:
    results = portal_catalog.searchResults({'portal_type' : 'Event', 'UID' : uid})
    if results:
        r = results[0]
        o = r.getObject()
        if hasattr(o, 'free_registration') and o.free_registration:
            from_email = getattr(o, 'contactEmail', 'do.not.reply@psu.edu')
            if from_email:
                from_email = "Penn State Extension <%s>" % from_email
            event_info = { 'event-name' : o.Title(),
                           'event-description' : o.Description(), 
                           'event-date' : r.start.strftime('%m/%d/%Y %I:%M %p'), 
                           'event-organizer-email' : o.free_registration_email or None,
                           'more-information' : o.absolute_url(),
                           'contact-email' : o.contactEmail or None,
                           'contact-name' : o.contactName or None,
                           'contact-phone' : o.contactPhone or None,
                           'from-email' : from_email,
                         }

for k in event_info.keys():
    request.form[k] = event_info[k]

return event_info

