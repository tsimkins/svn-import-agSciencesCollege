from zope import schema
from zope.interface import Interface

from zope.app.container.constraints import contains
from zope.app.container.constraints import containers

from Products.jobDescription import jobDescriptionMessageFactory as _

class IJobDescription(Interface):
    """Information about job Opportunities"""
    
    # -*- schema definition goes here -*-
    job_filled = schema.TextLine(
        title=_(u"Job Filled"), 
        required=False,
    )
    
    other_information = schema.TextLine(
        title=_(u"Other Information"), 
        required=False,
    )

    company_website = schema.TextLine(
        title=_(u"Company Website"), 
        required=False,
    )

    phone_number = schema.TextLine(
        title=_(u"Phone Number"), 
        required=False,
    )

    mailing_address = schema.Text(
        title=_(u"Mailing Address"), 
        required=False,
    )

    contact_email = schema.TextLine(
        title=_(u"Contact Email"), 
        required=True,
    )

    contact_title = schema.TextLine(
        title=_(u"Contact Title/Position"), 
        required=False,
    )

    contact_name = schema.TextLine(
        title=_(u"Contact Name"), 
        required=False,
    )

    company_name = schema.TextLine(
        title=_(u"Company Name"), 
        required=True,
    )

    job_website = schema.TextLine(
        title=_(u"Website for more information on this job"), 
        required=False,
    )

    application_deadline = schema.Date(
        title=_(u"Application Deadline"), 
        required=False,
    )

    application_instructions = schema.Text(
        title=_(u"Application Instructions"), 
        required=False,
    )

    job_related_disciplines = schema.TextLine(
        title=_(u"Related Disciplines"), 
        required=False,
    )

    job_description = schema.Text(
        title=_(u"Job Description"), 
        required=True,
    )

    job_type = schema.TextLine(
        title=_(u"Job Type"), 
        required=True,
    )

    job_status = schema.TextLine(
        title=_(u"Full or Part Time"), 
        required=True,
    )

    job_location = schema.TextLine(
        title=_(u"Location"), 
        required=True,
    )

class IJobDescriptionFolder(Interface):
    """Contains job descriptions"""
    
