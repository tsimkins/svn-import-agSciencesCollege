import feedparser
from datetime import datetime
from Products.CMFCore.utils import getToolByName
from zope.app.component.hooks import getSite

url = 'http://live.psu.edu/wirerss/69'
#url = 'http://webtools.cas.psu.edu/tmp/live.rss'

def sync(myContext):

	site = getSite()
	wftool =  getToolByName(site, 'portal_workflow')

	feed = feedparser.parse(url)

	theReturn = []

	for item in feed['entries']:
	
		title = item.get('title', None)
		summary = item.get('summary_detail', {}).get('value')
		link = item.get('links', [])[0].get('href', None)
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
			theArticle.reindexObject()
			
		else:
			theReturn.append("Skipped %s" % id)

	return theReturn
