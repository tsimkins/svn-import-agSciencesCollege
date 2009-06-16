#!/usr/bin/python

import re
from ploneimport import ploneify

# File Format (Tab Separated)
# start_date, end_date, title, description, url, location

def fromFile(fileName):
	
	createArgs = 6
	
	for line in open(fileName, 'r').readlines():
		data = [x.strip() for x in line.split("\t")]

		while len(data) < createArgs:
			data.append("")

		while len(data) > createArgs:
			data.pop()

		createEvent(*data)		

def createEvent(start_date, end_date, title, description, url, location):

	if not end_date:
		end_date = start_date

	id = ploneify(title)

	print """
context.invokeFactory(type_name="Event",
                id="%(id)s",
                title="%(title)s",
                start_date="%(start_date)s",
                end_date="%(end_date)s",
                event_url="%(url)s",
                location="%(location)s"
)""" % { "url" : url, "end_date" : end_date, "start_date" : start_date, "title" : title, "id": id, "location": location }

