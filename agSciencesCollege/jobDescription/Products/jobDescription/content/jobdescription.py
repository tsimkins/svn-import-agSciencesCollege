"""Definition of the JobDescription content type
"""

from zope.interface import implements, directlyProvides

from Products.Archetypes import atapi
from Products.ATContentTypes.content import base
from Products.ATContentTypes.content import schemata

from Products.jobDescription import jobDescriptionMessageFactory as _
from Products.jobDescription.interfaces import IJobDescription
from Products.jobDescription.config import PROJECTNAME

from zope.app.annotation.interfaces import IAttributeAnnotatable, IAnnotations
from persistent.list import PersistentList
from persistent.dict import PersistentDict
from datetime import datetime

from Acquisition import aq_parent

JobDescriptionSchema = schemata.ATContentTypeSchema.copy() + atapi.Schema((

    # -*- Your Archetypes field definitions here ... -*-

    atapi.StringField(
        'job_location',
        storage=atapi.AnnotationStorage(),
        widget=atapi.StringWidget(
            label=_(u"Location"),
        ),
        required=True,
    ),
    
    atapi.DateTimeField(
        'start_date',
        storage=atapi.AnnotationStorage(),
        widget=atapi.CalendarWidget(
            label=_(u"Start Date"),
        ),
        required=True,
        validators=('isValidDate'),
    ),

    atapi.DateTimeField(
        'end_date',
        storage=atapi.AnnotationStorage(),
        widget=atapi.CalendarWidget(
            label=_(u"End Date"),
        ),
        validators=('isValidDate'),
    ),
    
    atapi.StringField(
        'job_type',
        storage=atapi.AnnotationStorage(),
        widget=atapi.SelectionWidget(
            label=_(u"Job Type"),
            format='select'
        ),
        vocabulary=('Internship', 'Cooperative', 'Seasonal', 'Temporary', 'Permanent'),
        required=True,
    ),

    atapi.StringField(
        'job_status',
        storage=atapi.AnnotationStorage(),
        widget=atapi.SelectionWidget(
            label=_(u"Job Status"),
            format='radio',
        ),
        vocabulary = ('Full Time', 'Part Time'),
        required=True,
    ),

    atapi.TextField(
        'job_description',
        storage=atapi.AnnotationStorage(),
        widget=atapi.RichWidget(
            label=_(u"Job Description"),
        ),
        required=True,
        default_output_type='text/x-html-safe',
        validators=('isTidyHtmlWithCleanup',),
    ),

    atapi.TextField(
        'job_requirements',
        storage=atapi.AnnotationStorage(),
        widget=atapi.RichWidget(
            label=_(u"Job Requirements"),
        ),
        required=True,
        default_output_type='text/x-html-safe',
        validators=('isTidyHtmlWithCleanup',),
    ),

    atapi.StringField(
        'job_related_disciplines',
        storage=atapi.AnnotationStorage(),
        widget=atapi.MultiSelectionWidget(
            label=_(u"Related Disciplines"),
            format='checkbox'
        ),
        vocabulary="_getDisciplines",
    ),

    atapi.TextField(
        'application_instructions',
        storage=atapi.AnnotationStorage(),
        widget=atapi.RichWidget(
            label=_(u"Application Instructions"),
        ),
        default_output_type='text/x-html-safe',
        validators=('isTidyHtmlWithCleanup',),
    ),

    atapi.DateTimeField(
        'application_deadline',
        storage=atapi.AnnotationStorage(),
        widget=atapi.CalendarWidget(
            label=_(u"Application Deadline"),
        ),
        validators=('isValidDate'),
    ),

    atapi.StringField(
        'job_website',
        storage=atapi.AnnotationStorage(),
        widget=atapi.StringWidget(
            label=_(u"Website for more information on this job"),
        ),
    ),
    
    atapi.StringField(
        'company_name',
        storage=atapi.AnnotationStorage(),
        widget=atapi.StringWidget(
            label=_(u"Company Name"),
        ),
        required=True,
    ),

    atapi.StringField(
        'company_website',
        storage=atapi.AnnotationStorage(),
        widget=atapi.StringWidget(
            label=_(u"Company Website"),
        ),
    ),

    atapi.StringField(
        'contact_name',
        storage=atapi.AnnotationStorage(),
        widget=atapi.StringWidget(
            label=_(u"Contact Name"),
        ),
        required=True,
    ),

    atapi.StringField(
        'contact_title',
        storage=atapi.AnnotationStorage(),
        widget=atapi.StringWidget(
            label=_(u"Contact Title/Position"),
        ),
    ),

    atapi.StringField(
        'contact_email',
        storage=atapi.AnnotationStorage(),
        widget=atapi.StringWidget(
            label=_(u"Contact Email"),
        ),
        required=True,
        validators=('isEmail'),
    ),

    atapi.TextField(
        'mailing_address',
        storage=atapi.AnnotationStorage(),
        widget=atapi.TextAreaWidget(
            label=_(u"Mailing Address"),
        ),
    ),

    atapi.StringField(
        'phone_number',
        storage=atapi.AnnotationStorage(),
        widget=atapi.StringWidget(
            label=_(u"Phone Number"),
        ),
    ),

    atapi.StringField(
        'fax_number',
        storage=atapi.AnnotationStorage(),
        widget=atapi.StringWidget(
            label=_(u"Fax Number"),
        ),
    ),

    atapi.StringField(
        'other_information',
        storage=atapi.AnnotationStorage(),
        widget=atapi.StringWidget(
            label=_(u"Other Information"),
        ),
    ),
    
))

# Set storage on fields copied from ATContentTypeSchema, making sure
# they work well with the python bridge properties.

JobDescriptionSchema['title'].storage = atapi.AnnotationStorage()
JobDescriptionSchema['description'].storage = atapi.AnnotationStorage()

schemata.finalizeATCTSchema(JobDescriptionSchema, moveDiscussion=False)

class JobDescription(base.ATCTContent):
    """Information about job Opportunities"""
    implements(IJobDescription, IAttributeAnnotatable)

    meta_type = "JobDescription"
    schema = JobDescriptionSchema

    title = atapi.ATFieldProperty('title')
    description = atapi.ATFieldProperty('description')
    
    # -*- Your ATSchema to Python Property Bridges Here ... -*-
    other_information = atapi.ATFieldProperty('other_information')

    company_website = atapi.ATFieldProperty('company_website')

    fax_number = atapi.ATFieldProperty('fax_number')

    phone_number = atapi.ATFieldProperty('phone_number')

    mailing_address = atapi.ATFieldProperty('mailing_address')

    contact_email = atapi.ATFieldProperty('contact_email')

    contact_title = atapi.ATFieldProperty('contact_title')

    contact_name = atapi.ATFieldProperty('contact_name')

    company_name = atapi.ATFieldProperty('company_name')

    job_website = atapi.ATFieldProperty('job_website')

    application_deadline = atapi.ATFieldProperty('application_deadline')

    application_instructions = atapi.ATFieldProperty('application_instructions')

    job_related_disciplines = atapi.ATFieldProperty('job_related_disciplines')

    job_requirements = atapi.ATFieldProperty('job_requirements')

    job_description = atapi.ATFieldProperty('job_description')

    job_type = atapi.ATFieldProperty('job_type')
    
    job_status = atapi.ATFieldProperty('job_status')

    end_date = atapi.ATFieldProperty('end_date')

    start_date = atapi.ATFieldProperty('start_date')

    job_location = atapi.ATFieldProperty('job_location')

    # This stores who looks at the job description

	

    def addPageView(self, user):
        date = datetime.now()
        annotations = IAnnotations(self)

        if not annotations.get('jobDescription'):
            annotations['jobDescription'] = PersistentDict()
            annotations['jobDescription']['pageviews'] = PersistentList()
        
        annotations['jobDescription']['pageviews'].append([user, date])

        return "I added a pageview for %s on %s." % (user, date)
        
    def getPageViews(self):
        annotations = IAnnotations(self)

        if annotations.get('jobDescription'):
#            return reversed([(x,y.strftime('%m/%d/%Y')) for (x,y) in annotations['PAGEVIEWS']])
            return reversed([(x,y) for (x,y) in annotations['jobDescription']['pageviews']])

    # We're going to construct the vocabulary for the related disciplines from 
    # a field in the parent folder
    
    def _getDisciplines(self):
    
        vocab = aq_parent(self).getJob_related_disciplines().split('\r\n')
        return vocab


atapi.registerType(JobDescription, PROJECTNAME)
