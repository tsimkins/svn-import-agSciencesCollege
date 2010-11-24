#!/usr/bin/python

from ploneimport import commit

# File Format (Tab Separated)
# psu_id, last_name, first_name, middle_name, suffix, \
# email, office_address, city, state, zip, phone, job_title, \
# education, website

def fromFile(fileName, doCommit=True):
    
    createArgs = 14
    
    for line in open(fileName, 'r').readlines():

        if line.startswith("#"):
            continue
            
        data = [x.strip() for x in line.split("\t")]

        while len(data) < createArgs:
            data.append("")

        while len(data) > createArgs:
            data.pop()

        createPerson(*data)    
        
        if doCommit:
            commit()

def createPerson(psu_id, last_name, first_name, middle_name, suffix, 
                 email, office_address, city, state, zip, phone, 
                 job_title, education, website):

    print """
context.invokeFactory(type_name="FSDPerson", id='%(id)s', 
                        firstName='%(first_name)s', lastName='%(last_name)s',
                        suffix='%(suffix)s', email='%(email)s', officeAddress='%(office_address)s', 
                        officeCity='%(city)s', officeState='%(state)s', officePostalCode='%(zip)s', 
                        officePhone='%(phone)s', 
                        jobTitles='%(job_title)s', education='%(education)s', website='%(website)s', 
                        userpref_wysiwyg_editor='Kupu'
                        )
                        
context['%(id)s'].unmarkCreationFlag()

""" % { "id" : psu_id,  "first_name" : first_name, "last_name" : last_name, 
         "suffix" : suffix, "email" : email, "office_address" : office_address, 
         "city" : city, "state" : state, "zip" : zip, "phone" : phone, 
         "job_title" : job_title, "education" : education, "website" : website}