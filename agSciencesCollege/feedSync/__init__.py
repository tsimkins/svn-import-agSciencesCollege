import feedparser
from datetime import datetime
from Products.CMFCore.utils import getToolByName
from zope.app.component.hooks import getSite
from AccessControl.SecurityManagement import newSecurityManager
import urllib2
from urllib2 import HTTPError
from urlparse import urljoin
from BeautifulSoup import BeautifulSoup 
import time
from calendar import timegm
import re

from zope.component import getUtility
from plone.i18n.normalizer.interfaces import IIDNormalizer

url = 'http://news.psu.edu/rss/college/agricultural-sciences'

valid_tags = [
    'news-research', 
    'news-student-stories',
    'news-students',
    'news-international',
    'news-extension',
    'news-penn-state-extension'
]

IMAGE_FIELD_NAME = 'image'
IMAGE_CAPTION_FIELD_NAME = 'imageCaption'

def sync(myContext, url=url, valid_tags=valid_tags):
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
        description = item.get('summary_detail', {}).get('value')
        link = item.get('links', [])[0].get('href', None).split('#')[0]

        date_published_parsed = item.get('published_parsed')
        date_published = item.get('published')        
        
        dateStamp = datetime.now().strftime('%Y-%m-%d %H:%M')
        
        if date_published_parsed:
            local_time = time.localtime(timegm(date_published_parsed))
            dateStamp = time.strftime('%Y-%m-%d %H:%M', local_time)
        elif date_published:
            try:
                dateStamp = time.strftime('%Y-%m-%d %H:%M', time.strptime(date_published, '%A, %B %d, %Y - %H:%M'))
            except:
                pass

        id = str(link.split("/")[4]).split('#')[0]

        if not hasattr(myContext, id):
            myContext.invokeFactory(id=id,type_name="News Item",title=title, article_link=link, description=description)
            theReturn.append("Created %s" % id)
            
            theArticle = getattr(myContext, id)
            
            
            # http://plone.org/documentation/how-to/set-creation-date
            theArticle.setCreationDate(dateStamp)
            theArticle.setModificationDate(dateStamp)
            theArticle.setEffectiveDate(dateStamp)
                        
            theArticle.setExcludeFromNav(True)

            # Grab article image and set it as contentleadimage
            html = getHTML(link)
            tags = getTags(html, valid_tags=valid_tags)
            if tags:
                theArticle.setSubject(tags)
            setImage(theArticle, html=html)

            # Set the body text
            body_text = getBodyText(html)
            theArticle.setText(body_text)

            # Publish
            if wftool.getInfoFor(theArticle, 'review_state') != 'Published':
                wftool.doActionFor(theArticle, 'publish')

            theArticle.indexObject()
            
        else:
            theReturn.append("Skipped %s" % id)

    return theReturn

def getBodyText(html):
    mySoup = BeautifulSoup(html)
    try:
        body = mySoup.find("div", {'class' : re.compile('field-name-body')})
        item = body.find("div", {'class' : re.compile('field-item($|\s+)')})
    except:
        return ""

    return item.renderContents()

def getTags(html, valid_tags=[]):
    mySoup = BeautifulSoup(html)
    normalizer = getUtility(IIDNormalizer)
    try:
        tags_div = mySoup.find("div", {'class' : re.compile('views-field-field-tags')})
        items = tags_div.findAll("a", {'typeof' : re.compile('skos:Concept')})
        article_tags = [normalizer.normalize(str(x.contents[0])).strip() for x in items]
        if valid_tags:
            tags = set(valid_tags) & set(article_tags)
        else:
            tags = list(article_tags)
        return ['news-%s' % x for x in list(tags)]
    except:
        return []


def htmlToPlainText(html):
    site = getSite()
    portal_transforms = getToolByName(site, 'portal_transforms')
    return portal_transforms.convert('html_to_text', html).getData().replace("\n", '').strip()

def getHTML(url):
    try:
        return urllib2.urlopen(url).read()
    except HTTPError:
        print "404 for %s" % url 
        return ""


def getImageAndCaption(html=None, url=None):

    if not (html or url):
        return (None, None)
    elif not html:
        html = getHTML(url)

    mySoup = BeautifulSoup(html)

    img_url = ""
    img_caption = ""
    imgSrc = ""
    
    for div in mySoup.findAll("div", {'class' : 'image'}):
        for img in div.findAll("img"):
            img_url = img.get('src')
            if img_url:
                parent = div.parent
                for caption in parent.findAll("div", {'class' : 'caption'}):
                    img_caption = htmlToPlainText(caption.prettify())
                    if img_caption:
                        break
                if not img_caption:
                    for span in div.findAll("span", {'property' : 'dc:title'}):
                        img_caption = span.get('content')
                        if img_caption:
                            break
        if img_url:
            break

    if not img_url:
        img_caption = ""
        for ul in mySoup.findAll("ul", {'class' : 'slides'}):
            for li in ul.findAll('li'):
                try:
                    img_url = li.find("div", {'class' : re.compile('field-name-field-image')}).find("img").get('src')
                    img_caption = htmlToPlainText(li.find("div", {'class' : re.compile('field-name-field-flickr-description')}).prettify())
                except:
                    pass
                if img_url:
                    break
    if img_url:
        imgSrc = urljoin(url, img_url)

    if imgSrc:
        imgData = downloadImage(imgSrc)        
        return (imgData, img_caption)
    else:
        return (None, None)

def hasImage(context):
    image_field = context.getField(IMAGE_FIELD_NAME).get(context)
    
    if image_field and image_field.size:
        return True
    else:
        return False

def downloadImage(url):
    try:
        imgFile = urllib2.urlopen(url)
    except HTTPError:
        return None
    else:
        imgData = imgFile.read()            
        return imgData

def setImage(theArticle, image_url=None, html=None):
    # Given an article, and either an image URL or a set of HTML, sets the image
    # and caption for the article.

    theImage = theImageCaption = ""

    if image_url:
        theImage = downloadImage(image_url)
        theImageCaption = ""
    else:
        if not html:
            if hasattr(theArticle, 'getRemoteUrl'):
                url = theArticle.getRemoteUrl()
            elif hasattr(theArticle, 'article_link'):
                url = theArticle.article_link
            else:
                url = None

            if url:
                html = getHTML(url)            
            else:
                return None

        # Grab article image and caption
        (theImage, theImageCaption) = getImageAndCaption(html=html)

    if theImage:
        theArticle.getField(IMAGE_FIELD_NAME).set(theArticle, theImage)
        theArticle.getField(IMAGE_CAPTION_FIELD_NAME).set(theArticle, theImageCaption)
        theArticle.reindexObject()
        print "setImage for %s" % theArticle.id
    else:
        print "No Image for %s" % theArticle.id


        
def retroSetImages(context):
    for theArticle in context.listFolderContents(contentFilter={"portal_type" : "News Item"}):
    
        setImage(theArticle)
