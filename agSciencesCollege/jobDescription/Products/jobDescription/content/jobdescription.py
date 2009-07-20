"""Definition of the JobDescription content type
"""

from zope.interface import implements, directlyProvides

from Products.Archetypes import atapi
from Products.ATContentTypes.content import base
from Products.ATContentTypes.content import schemata

from Products.jobDescription import jobDescriptionMessageFactory as _
from Products.jobDescription.interfaces import IJobDescription
from Products.jobDescription.config import PROJECTNAME

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
        required=True,
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
    ),

    atapi.TextField(
        'job_requirements',
        storage=atapi.AnnotationStorage(),
        widget=atapi.RichWidget(
            label=_(u"Job Requirements"),
        ),
        required=True,
    ),

    atapi.StringField(
        'job_related_disciplines',
        storage=atapi.AnnotationStorage(),
        widget=atapi.MultiSelectionWidget(
            label=_(u"Related Disciplines"),
            format='checkbox'
        ),
        vocabulary=sorted(('Agribusiness Management', 'Agricultural and Extension Education', 'Agricultural Science', 'Agricultural Systems Management', 'Agroecology', 'Animal Sciences', 'Biological Engineering', 'Community, Environment, and Development', 'Environmental Resource Management', 'Environmental Soil Science', 'Food Science', 'Forest Science', 'Horticulture', 'Immunology and Infectious Disease', 'Landscape Contracting', 'Toxicology', 'Turfgrass Science', 'Veterinary and Biomedical Sciences', 'Wildlife and Fisheries Science', 'Wood Products')
    )),

    atapi.TextField(
        'application_instructions',
        storage=atapi.AnnotationStorage(),
        widget=atapi.RichWidget(
            label=_(u"Application Instructions"),
        ),
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
    implements(IJobDescription)

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


atapi.registerType(JobDescription, PROJECTNAME)
