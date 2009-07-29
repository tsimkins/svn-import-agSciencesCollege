"""Definition of the JobDescriptionFolder content type
"""

from zope.interface import implements, directlyProvides

from Products.Archetypes import atapi
from Products.ATContentTypes.content import folder
from Products.ATContentTypes.content import schemata

from Products.jobDescription import jobDescriptionMessageFactory as _
from Products.jobDescription.interfaces import IJobDescriptionFolder
from Products.jobDescription.config import PROJECTNAME

JobDescriptionFolderSchema = folder.ATFolderSchema.copy() + atapi.Schema((

    # -*- Your Archetypes field definitions here ... -*-
    atapi.TextField(
        'job_related_disciplines',
        storage=atapi.AnnotationStorage(),
        widget=atapi.TextAreaWidget(
            label=_(u"Related Disciplines"),
        ),
        required=True,
    ),    

))

# Set storage on fields copied from ATFolderSchema, making sure
# they work well with the python bridge properties.

JobDescriptionFolderSchema['title'].storage = atapi.AnnotationStorage()
JobDescriptionFolderSchema['description'].storage = atapi.AnnotationStorage()

schemata.finalizeATCTSchema(JobDescriptionFolderSchema, folderish=True, moveDiscussion=False)

class JobDescriptionFolder(folder.ATFolder):
    """A folder that contains job descriptions"""
    implements(IJobDescriptionFolder)

    portal_type = "JobDescriptionFolder"
    schema = JobDescriptionFolderSchema

    title = atapi.ATFieldProperty('title')
    description = atapi.ATFieldProperty('description')
    job_related_disciplines = atapi.ATFieldProperty('job_related_disciplines')
    
    def getSortedEntries(self):
        return sorted(self.listFolderContents(contentFilter={'portal_type' : 'JobDescription'}), key=lambda (x): x.Title())

atapi.registerType(JobDescriptionFolder, PROJECTNAME)
