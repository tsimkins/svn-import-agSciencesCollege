#!/usr/bin/python

# Zope imports
from zope.component import getSiteManager
from Products.CMFCore.utils import getToolByName
from AccessControl.SecurityManagement import newSecurityManager
#import transaction

# My imports
import pdb
from BeautifulSoup import BeautifulSoup
from time import strptime, strftime
import urllib2
import sys
import re

def importEvents(context, emailUsers=['trs22']):
    myStatus = []
    newEvents = []

    cventURL = "http://guest.cvent.com/EVENTS/Calendar/Calendar.aspx?cal=9d9ed7b8-dd56-46d5-b5b3-8fb79e05acaf"
    summaryURL = "http://guest.cvent.com/EVENTS/info/summary.aspx?e=%s"
    conferenceURL="https://agsci.psu.edu/conferences/event-calendar"

    # More Zopey goodness
    
    admin = context.acl_users.getUserById('trs22')
    admin = admin.__of__(context.acl_users)
    newSecurityManager(None, admin) 
    
    portal = getSiteManager(context)
    
    # Grab CVENT data and create events
    page = urllib2.urlopen(cventURL)
    myHTML = "\n".join(page).replace(r'\"', '"')
    soup = BeautifulSoup(myHTML)
    cventIDs = []
    
    # Get listing of events, and their cventid if it exists
    for myEvent in context.listFolderContents(contentFilter={"portal_type" : "Event"}):
        cventIDs.append(myEvent.id)
        myCventID = myEvent.getProperty('cventid')
        if myCventID:
            cventIDs.append(myCventID)
    
    for eventRow in soup.findAll('table', {'class':'calLinks'}):
    
        dateCell = eventRow.find('td', {'class':'BodyTextBold1'})
        
        eventDate = strftime("%Y-%m-%d", strptime(dateCell.contents[0].strip(), "%B %d, %Y"))
        
        for eventCell in eventRow.findAll('td', {'class':'BodyText1'}):
            eventLink = eventCell.find('a')
            eventId = eventLink['e']
            eventTitle = str(eventLink.contents[0])
            eventURL = summaryURL % eventId
        
            if not cventIDs.count(eventId):
        
                newEvents.append("<li><a href=\"%s/%s\">%s</a></li>" % (conferenceURL, eventId, eventLink.contents[0]))
        
                context.invokeFactory(type_name="Event",
                        id=eventId,
                        title=eventTitle,
                        start_date=eventDate,
                        end_date=eventDate,
                        event_url=eventURL,
                        location="")  
    
                myObject = getattr(context, eventId)
                myObject.manage_addProperty('cventid', eventId, 'string')
                myObject.setExcludeFromNav(True)
                myObject.reindexObject()
        
                myStatus.append("Created event %s (id %s)" % (eventTitle, eventId))
    
            else:
                myStatus.append("Skipped event %s (id %s)" % (eventTitle, eventId))
                #newEvents.append("<li>NOT: <a href=\"%s/%s\">%s</a></li>" % (conferenceURL, eventId, eventLink.contents[0]))

    if newEvents:
        myStatus.append("Sending email to: %s" % ", ".join(emailUsers))
        mFrom = "do.not.reply@psu.edu"
        mSubj = "CVENT Events Imported"
        mTitle = "<p><strong>The following events from cvent have been imported.</strong></p>"
        statusText = "\n".join(newEvents)
        mailHost = context.MailHost

        for myUser in emailUsers:
            mTo = "%s@psu.edu" % myUser
        
            mMsg = "\n".join(["\n\n", mTitle, "<ul>", statusText, "<ul>"])
            mailHost.secureSend(mMsg, mto=mTo, mfrom=mFrom, subject=mSubj, subtype='html')

    #transaction.commit()
    myStatus.append("Finished Loading")
    return "\n".join(myStatus)
    #return newEvents
