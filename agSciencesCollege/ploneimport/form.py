#!/usr/bin/python

from ploneimport import ploneify, commit

# File Format (Tab Separated)
# id, fieldset, type, title, description
# Node that there can be only one FormFolder.  Like the Highlander.
# The FormFolder should be the first line.

formFolderId = None

def fromFile(fileName, doCommit=True):
    
    createArgs = 5
    
    for line in open(fileName, 'r').readlines():

        if line.startswith("#"):
            continue
            
        data = [x.strip() for x in line.split("\t")]

        while len(data) < createArgs:
            data.append("")

        while len(data) > createArgs:
            data.pop()

        createForm(*data)
        
        if doCommit:
            commit()    

def createForm(id, fieldset, type, title, description):
    global formFolderId
    valid_types = {
        'FormFolder' : 'Form Folder',
        'FormBooleanField' : 'Checkbox Field',
        'FormDateField' : 'Date/Time Field',
        'FormFixedPointField' : 'Decimal Number Field',
        'FieldsetFolder' : 'Fieldset Folder',
        'FormFileField' : 'File Field',
        'FormLabelField' : 'Label Field',
        'FormLinesField' : 'Lines Field',
        'FormMultiSelectionField' : 'Multi-Select Field',
        'FormPasswordField' : 'Password Field',
        'FormLikertField' : 'Rating-Scale Field',
        'FormRichLabelField' : 'Rich Label Field',
        'FormRichTextField' : 'RichText Field',
        'FormSelectionField' : 'Selection Field',
        'FormStringField' : 'String Field',
        'FormTextField' : 'Text Field',
        'FormIntegerField' : 'Whole Number Field',
    }

    if not id.strip():
        id = ploneify(title)

    if not type in valid_types.keys():
        print "# Invalid type %s" % type
        return False
    elif not formFolderId and type != 'FormFolder':
        print "# No form folder created"
        return False

    if type == 'FormFolder':
        formFolderId = id
        print """myContext = context"""
    elif fieldset:
        print """myContext = context['%s']['%s']""" % (formFolderId, fieldset)
    else:
        print """myContext = context['%s']""" % formFolderId  

    print """myContext.invokeFactory(type_name="%(type)s",
                id="%(id)s",
                title="%(title)s",
                description="%(description)s")""" % { "title" : title, "id": id, "type" : type, "description" : description }

    # Remove default fields
    if type == 'FormFolder': 
        print """myContext['%s'].manage_delObjects(ids=['replyto', 'topic', 'comments'])""" % id
    
  



