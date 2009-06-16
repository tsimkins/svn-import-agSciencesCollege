#!/usr/bin/python

import re
from ploneimport import ploneify, comment, getFlags, setContext, excludeFromNav, publish, setAsDefault, commit

# File Format (Tab Separated)
# content_type, flags, old_url, url, title, description, html
# Note that we assume that the urls are sorted in sequential order!
# In other words, you can't create a page within a folder that
# hasn't been created.  Generally, an ASC sort will do this.

importFunction = lambda x: "Content from %s goes here." % x


def setImportFunction(f):
	global importFunction
	importFunction = f

def fromFile(fileName):
	
	createArgs = 7

	for line in open(fileName, 'r').readlines():

		if line.startswith("#"):
			continue

		data = [x.strip() for x in line.split("\t")]

		while len(data) < createArgs:
			data.append("")

		while len(data) > createArgs:
			data.pop()

		content_type = data.pop(0)
		data[0] = (getFlags(data[0]))
		
		if content_type.lower() == 'page':
			createPage(*data)
		elif content_type.lower() == 'link':
			createLink(*data)
		elif content_type.lower() == 'folder':
			createFolder(*data)
		
		commit()

def createPage(flags={}, old_url="", url="", title="", description="", html=""):

	comment("Creating page %s" %  url)

	id = url.split("/").pop().strip()
	
	setContext(url)
	
	if old_url:
		html = importFunction(old_url)
	
	print """myContext.invokeFactory(id="%(id)s", 
		type_name="Document", 
		title="%(title)s", 
		description = "%(description)s",
		text='''%(html)s''')""" % { "id" : id, "title" : title, "description" : description, "html" : html }

	processFlags(id, flags)

def createLink(flags={}, remote_url="", location="", title="", description="", html=""):

	comment("Creating link %s" %  remote_url)

	id = ploneify(title)
	
	setContext(location + "/" + id)
	
	print """myContext.invokeFactory(id="%(id)s", 
		type_name="Link", 
		title="%(title)s", 
		description = "%(description)s",
		remote_url='''%(remote_url)s''')""" % { "id" : id, "title" : title, "description" : description, "remote_url" : remote_url }

	processFlags(id, flags)

	
def createFolder(flags={}, old_url="", url="", title="", description="", html=""):

	comment("Creating folder %s" %  url)

	id = url.split("/").pop().strip()
	
	setContext(url)
	
	print """myContext.invokeFactory(id="%(id)s", 
		type_name="Folder", 
		title="%(title)s", 
		description = "%(description)s")""" % { "id" : id, "title" : title, "description" : description }

	processFlags(id, flags)
	
	if old_url or html:

		createPage(flags={"isdefault" : True }, old_url=old_url, url=url + "/default", title=title, description=description, html=html)



def processFlags(id, flags):

	if flags.get("excludefromnavigation"):
		excludeFromNav(id)

	if not flags.get("private"):
		publish(id)
		
	if flags.get("isdefault"):
		setAsDefault(id)

