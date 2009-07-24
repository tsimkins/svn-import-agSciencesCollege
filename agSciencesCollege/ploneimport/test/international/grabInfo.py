#!/usr/bin/python

import urllib2
from BeautifulSoup import BeautifulSoup 
import re
import sys
import pdb
from ploneimport import ploneify

def getInfo(url):
	
	mySoup = BeautifulSoup(urllib2.urlopen(url))

	myTitle =  mySoup.find('title').contents[0].strip().replace("CAS - International Programs - ", "").replace('&amp;', 'and')
	myBreadcrumbs = mySoup.find('div', id="breadcrumbs")
	
	myPath = []
	
	for myLink in myBreadcrumbs.findAll('a'):
		myText = myLink.contents[0].strip().replace('&amp;', 'and')
		myText = ploneify(myText, uniq=False)
		
		myPath.append(myText)

	myLocation = ploneify(myTitle, uniq=False)
	myPath.append(myLocation)
	
	myURL = "/".join(myPath)
	
	replacePath = re.compile('^psu/agsci/international-programs', re.I|re.M)
	myURL = replacePath.sub('', myURL)
	
	return (url, myURL, myTitle)

for url in open("urls", 'r').readlines():

	try:
		myData = getInfo(url.strip())
		print "\t".join(myData)
	except IndexError:
		print "IndexError with %s" % url
	except AttributeError:
		print "AttributeError with %s" % url
