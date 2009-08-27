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

    atapi.TextField(
        'flag_after_days',
        storage=atapi.AnnotationStorage(),
        widget=atapi.IntegerWidget(
            label=_(u"Flag jobs after being posted for this many days."),
        ),
        default=14,
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
        openJobs = []
        jobList = sorted(self.listFolderContents(contentFilter={'portal_type' : 'JobDescription'}), key=lambda (x): x.EffectiveDate())
        for job in reversed(jobList):
            if not job.job_filled:
                openJobs.append(job)

        return openJobs

atapi.registerType(JobDescriptionFolder, PROJECTNAME)
