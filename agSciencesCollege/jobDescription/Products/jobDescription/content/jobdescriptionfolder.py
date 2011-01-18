"""Definition of the JobDescriptionFolder content type
"""

from zope.interface import implements, directlyProvides

from Products.Archetypes import atapi
from Products.ATContentTypes.content import folder
from Products.ATContentTypes.content import schemata

from Products.jobDescription import jobDescriptionMessageFactory as _
from Products.jobDescription.interfaces import IJobDescriptionFolder
from Products.jobDescription.config import PROJECTNAME

from DateTime import DateTime

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
        default='14',
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
    flag_after_days = atapi.ATFieldProperty('flag_after_days')

    def canModifyPortalContent(self):
        mtool = self.portal_membership
        # checkPermissions returns true if permission is granted

        return mtool.checkPermission('Modify portal content', self)
        
    def getSortedEntries(self):
        openJobs = []
        jobList = sorted(self.listFolderContents(contentFilter={'portal_type' : 'JobDescription'}), key=lambda (x): x.EffectiveDate())
        for job in reversed(jobList):
            if ((job.application_deadline and DateTime() <= job.application_deadline + 1) or not job.application_deadline) and not job.job_filled:
                openJobs.append(job)

        return openJobs
        
    def getPageviewsReport(self):
        results = [['Job Id', 'Job Title', 'User Id', 'Date'],]
        jobList = sorted(self.listFolderContents(contentFilter={'portal_type' : 'JobDescription'}), key=lambda (x): x.EffectiveDate())

        for job in reversed(jobList):
            pageviews = job.getPageViews()
            title = job.Title().strip()

            if pageviews:
                for (userid, datestamp) in pageviews:
                    results.append([job.id, title, userid, datestamp.strftime('%m-%d-%Y')])
            else:
                results.append([job.id, title, 'N/A', 'N/A'])

        return results
        
atapi.registerType(JobDescriptionFolder, PROJECTNAME)
