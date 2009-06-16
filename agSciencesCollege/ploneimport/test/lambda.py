#!/usr/bin/python

import urllib2
from BeautifulSoup import BeautifulSoup 
import re

baseURL = "http://www.sfr.psu.edu"

def getContent(url):
	
	myURL = baseURL + url
	mySoup = BeautifulSoup(urllib2.urlopen(myURL))
 
 	myOuterTable = mySoup.findAll('table')[0]
 	myOuterTr = myOuterTable.findAll('tr')[3]
 	myOuterTd = myOuterTr.findAll('td')[1]
 	myInnerTable = myOuterTd.findAll('table')[0]
 	myTd = myInnerTable.findAll('td')[0].prettify()

	removeTags = re.compile('</*(blockquote|span|font|center|hr).*?>', re.I|re.M)	
	removeAttributes = re.compile('\s*(id|width|height|align|valign|class)\s*=\s*".*?"', re.I|re.M)
	removeBR = re.compile(r'(>*)<br />(<*)', re.I|re.M)
	removeTd = re.compile('(^<td.*?>|</td>$)', re.I|re.M)
	
	myTd = removeTd.sub("", myTd)
	myTd = removeTags.sub("", myTd)
	myTd = removeAttributes.sub("", myTd)
	myTd = removeBR.sub("\1 \2", myTd)
		
	return myTd
	


myFunc = lambda x: getContent(x)

print myFunc("/GeneralPublic.html")