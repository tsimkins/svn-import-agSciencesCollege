import feedparser
from datetime import datetime
from Products.CMFCore.utils import getToolByName
from zope.app.component.hooks import getSite
from AccessControl.SecurityManagement import newSecurityManager
import urllib2
from urllib2 import HTTPError
from BeautifulSoup import BeautifulSoup 
from collective.contentleadimage.config import IMAGE_FIELD_NAME

url = 'http://live.psu.edu/wirerss/69'

def sync(myContext):
    # Be an admin
    admin = myContext.acl_users.getUserById('trs22')
    admin = admin.__of__(myContext.acl_users)
    newSecurityManager(None, admin) 

    print "Syncing RSS feeds from %s" % url
    site = getSite()
    wftool =  getToolByName(site, 'portal_workflow')

    feed = feedparser.parse(url)

    theReturn = []

    for item in feed['entries']:
    
        title = item.get('title', None)
        summary = item.get('summary_detail', {}).get('value')
        link = item.get('links', [])[0].get('href', None).replace('#rss69', '')
        dateArray = list(item.get('updated_parsed')[0:7])
        dateArray[3] = int(item.get('updated').split(' ')[4].split(':')[0])
    
        date = datetime(*dateArray)
        dateStamp = str(date)
        id = str(link.split("/")[4])
    

        if not hasattr(myContext, id):
            myContext.invokeFactory(id=id,type_name="Link",title=title, remote_url=link, description=summary)
            theReturn.append("Created %s" % id)
            
            theArticle = getattr(myContext, id)
            
            if wftool.getInfoFor(theArticle, 'review_state') != 'Published':
                wftool.doActionFor(theArticle, 'publish')
            
            
            # http://plone.org/documentation/how-to/set-creation-date
            theArticle.setCreationDate(dateStamp)
            theArticle.setModificationDate(dateStamp)
            theArticle.setEffectiveDate(dateStamp)
                        
            theArticle.setExcludeFromNav(True)

            # Grab article image and set it as contentleadimage            
            theImage = getImage(link)

            if theImage:
                theArticle.getField(IMAGE_FIELD_NAME).set(theArticle, theImage)
            
            theArticle.indexObject()
            
        else:
            theReturn.append("Skipped %s" % id)

    return theReturn

def getImage(url):

    try:
        mySoup = BeautifulSoup(urllib2.urlopen(url))
    except HTTPError:
        print "404 for %s" % url
        return None
        
    myImg = mySoup.findAll(id="article_image")
    
    if myImg:
        imgSrc = "http://live.psu.edu%s"%  myImg[0]['src']
        
        try:
            imgFile = urllib2.urlopen(imgSrc)
        except HTTPError:
            return None
        else:
            imgData = imgFile.read()            
            return imgData

def setImage(theArticle):
    url = theArticle.getRemoteUrl()

    # Grab article image and set it as contentleadimage            
    theImage = getImage(url)

    if theImage:
        theArticle.getField(IMAGE_FIELD_NAME).set(theArticle, theImage)
        theArticle.reindexObject()
        print "setImage for %s" % theArticle.id
    else:
        print "No Image for %s" % theArticle.id


        
def retroSetImages(context):
    for theArticle in context.listFolderContents(contentFilter={"portal_type" : "Link"}):
    
        setImage(theArticle)