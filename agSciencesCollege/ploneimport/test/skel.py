#!/usr/bin/python

import urllib2
from BeautifulSoup import BeautifulSoup 
import re
import ploneimport.skeleton
import sys
#import pdb

def scrub(html):

	htmlEntities = [
		["&#8211;", "--"],
		["&#8220;", '"'],
		["&#8221;", '"'],
		["&#8216;", "'"],
		["&#8217;", "'"],
		["&#146;", "'"],
		["&nbsp;", " "],
	]

	for ent in htmlEntities:
		html = html.replace(ent[0], ent[1])
	
	return html

def getSFRContent(url):
	
	mySoup = BeautifulSoup(urllib2.urlopen(url))
 
 	myOuterTable = mySoup.findAll('table')[0]
 	myOuterTr = myOuterTable.findAll('tr')[3]
 	myOuterTd = myOuterTr.findAll('td')[1]
 	myInnerTable = myOuterTd.findAll('table')[0]
 	myTd = myInnerTable.findAll('td')[0].prettify()

	removeTags = re.compile('</*(blockquote|span|font|center|hr|div).*?>', re.I|re.M)
	removeSingleTags = re.compile('</*(u|b|strong|em|i)>', re.I|re.M)	
	removeAttributes = re.compile('\s*(id|width|height|align|valign|class|style)\s*=\s*".*?"', re.I|re.M)
	removeBR = re.compile('<br />', re.I|re.M)
	removeTd = re.compile('(^<td.*?>|</td>$)', re.I|re.M)
	removeSpaces = re.compile('\s+', re.I|re.M)
	
	myTd = removeTd.sub("", myTd)
	myTd = removeTags.sub("", myTd)
	myTd = removeSingleTags.sub("", myTd)
	myTd = removeAttributes.sub("", myTd)
	myTd = removeBR.sub(" ", myTd)
	myTd = removeSpaces.sub(" ", myTd)
	
	myTd = myTd.replace("\r", "")
	
	myTd = scrub(myTd)
	
	return myTd
	
def getGrantsContent(url):
	
	mySoup = BeautifulSoup(urllib2.urlopen(url))
 
 	myCenterColumn = mySoup.find('div', id="centercolumn")
 	myContent = mySoup.find('div', id="content")

	myHTML = "No Content Found for %s" % url

	if myCenterColumn:
		myHTML = myCenterColumn.prettify()
	elif myContent:
		for h1 in myContent.findAll('h1'):
			h1.extract()
		for div in myContent.find('div', id="unit"):
			div.extract()	
		myHTML = myContent.prettify()	


	removeTags = re.compile('</*(blockquote|span|font|center|hr|div).*?>', re.I|re.M)
	removeSingleTags = re.compile('</*(u|b|strong|em|i)>', re.I|re.M)	
	removeAttributes = re.compile('\s*(id|width|height|align|valign|class|type)\s*=\s*".*?"', re.I|re.M)
	removeBR = re.compile('<br />', re.I|re.M)
	removeTd = re.compile('(^<td.*?>|</td>$)', re.I|re.M)
	removeSpaces = re.compile('\s+', re.I|re.M)
	removeEmptyP = re.compile('<p>\s*</p>', re.I|re.M)
	removeComments = re.compile('<!--.*?-->', re.I|re.M)

	myHTML = scrub(myHTML)
	
	myHTML = myHTML.replace("\r", " ")	
	myHTML = removeTd.sub("", myHTML)
	myHTML = removeTags.sub("", myHTML)
	myHTML = removeSingleTags.sub("", myHTML)
	myHTML = removeAttributes.sub("", myHTML)
	myHTML = removeBR.sub(" ", myHTML)
	#pdb.set_trace()
	myHTML = removeEmptyP.sub("", myHTML)
	myHTML = removeComments.sub("", myHTML)
	myHTML = removeSpaces.sub(" ", myHTML)			


	

	
	return myHTML


#ploneimport.skeleton.setImportFunction(lambda x: getContent(x))
#ploneimport.skeleton.setImportFunction(lambda x: "FOO %s" % x)

ploneimport.setLocation('agsci.psu.edu', '/grants')
ploneimport.skeleton.setImportFunction(lambda x: getGrantsContent(x))
ploneimport.skeleton.fromFile('skel')
