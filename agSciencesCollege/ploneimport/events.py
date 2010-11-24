#!/usr/bin/python

from ploneimport import ploneify, commit

# File Format (Tab Separated)
# start_date, end_date, title, description, url, location, sub_type

def fromFile(fileName, doCommit=True):
    
    createArgs = 7
    
    for line in open(fileName, 'r').readlines():

        if line.startswith("#"):
            continue

        data = [x.strip() for x in line.split("\t")]

        while len(data) < createArgs:
            data.append("")

        while len(data) > createArgs:
            data.pop()

        createEvent(*data)
        
        if doCommit:
            commit()    

def createEvent(start_datestamp, end_datestamp, title, description, url, location, sub_type):

    if not end_datestamp:
        end_datestamp = start_datestamp
        
    if not sub_type:
        sub_type = "Event"


    start = start_datestamp.split()
    end = end_datestamp.split()
    
    if len(start) == 1:
        start_date = start[0]    
        start_time = ''
    else:
        start_date = start[0]    
        start_time = start[1]


    if len(end) == 1:
        end_date = end[0]    
        stop_time = ''
    else:
        end_date = end[0]    
        stop_time = end[1]
        
    id = ploneify(title)

    print """
context.invokeFactory(type_name="%(sub_type)s",
                id="%(id)s",
                title="%(title)s",
                start_date="%(start_date)s",
                start_time="%(start_time)s",
                end_date="%(end_date)s",
                stop_time="%(stop_time)s",
                event_url="%(url)s",
                location="%(location)s"
)""" % { "url" : url, "end_date" : end_date, "start_date" : start_date, 
         "stop_time" : stop_time, "start_time" : start_time,
         "title" : title, "id": id, "location": location, "sub_type" : sub_type }


