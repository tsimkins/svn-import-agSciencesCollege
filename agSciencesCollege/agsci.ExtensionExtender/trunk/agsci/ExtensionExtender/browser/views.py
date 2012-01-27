from zope.interface import implements, Interface
from Products.Five import BrowserView
from Products.CMFCore.utils import getToolByName
from Acquisition import aq_acquire, aq_inner
from collective.contentleadimage.config import IMAGE_FIELD_NAME, IMAGE_CAPTION_FIELD_NAME
from DateTime import DateTime
from urllib import urlencode
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
import premailer
from BeautifulSoup import BeautifulSoup
from zope.component import getUtility, getMultiAdapter
from collective.contentleadimage.leadimageprefs import ILeadImagePrefsForm
from Products.agCommon.browser.views import FolderView
import re

from Products.CMFPlone.interfaces import IPloneSiteRoot

class IExtensionProgramCountyView(Interface):
    """
    Program County view interface
    """

    def test():
        """ test method"""

class ExtensionProgramCountyView(FolderView):
    """
    Program County browser view
    """
    implements(IExtensionProgramCountyView)
    
    def __init__(self, context, request):
        self.context = context
        self.request = request
        
        programs = {}
        counties = {}
        
        portal_catalog = self.portal_catalog

        all_programs = self.request.form.get('program')
        
        if not all_programs:
            all_programs = portal_catalog.uniqueValuesFor('Programs')
        elif isinstance(all_programs, str):
            all_programs = [all_programs]

        all_counties = self.request.form.get('county')
        
        if not all_counties:
            all_counties = portal_catalog.uniqueValuesFor('Counties')
        elif isinstance(all_counties, str):
            all_counties = [all_counties]
        
        for p in all_programs:
            programs[p] = {}
            for c in all_counties:
                programs[p][c] = []

        for c in all_counties:
            counties[c] = {}
            for p in all_programs:
                counties[c][p] = []
        
        for r in portal_catalog.searchResults({'portal_type' : 'FSDPerson'}):
            for p in r.extension_programs:
                for c in r.extension_counties:
                    if p in all_programs and c in all_counties:
                        programs[p][c].append(r)
                        counties[c][p].append(r)                  

        self.by_program = programs
        self.by_county = counties
        
    def getBodyText(self):
        return self.context.getBodyText()

    @property
    def portal_catalog(self):
        return getToolByName(self.context, 'portal_catalog')

    @property
    def portal(self):
        return getToolByName(self.context, 'portal_url').getPortalObject()
