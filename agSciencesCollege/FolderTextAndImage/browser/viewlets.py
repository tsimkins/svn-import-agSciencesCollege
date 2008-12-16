from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.app.layout.viewlets.common import ViewletBase
from zope.component import getMultiAdapter
from Products.Archetypes.BaseObject import BaseObject
from Acquisition import aq_base

class FolderImageViewlet(ViewletBase):
	render = ViewPageTemplateFile('folder_image.pt')

	def update(self):
		
		# Define self.folder_image and various sizes

		# Acquisition.aq_base strips the acquisition layer from an object.
		# See: https://weblion.psu.edu/trac/weblion/wiki/OverridingPloneAcquisition
		my_context = aq_base(self.context)

		try:
			self.folder_image = my_context.folder_image.tag(css_class = 'folder_image')
			self.folder_image_large = my_context.getWrappedField("folder_image").tag(my_context, scale='large', css_class = 'folder_image')
			self.folder_image_preview = my_context.getWrappedField("folder_image").tag(my_context, scale='preview', css_class = 'folder_image')
			self.folder_image_mini = my_context.getWrappedField("folder_image").tag(my_context, scale='mini', css_class = 'folder_image')
			self.folder_image_thumb = my_context.getWrappedField("folder_image").tag(my_context, scale='thumb', css_class = 'folder_image')
			self.folder_image_tile = my_context.getWrappedField("folder_image").tag(my_context, scale='tile', css_class = 'folder_image')
			self.folder_image_icon = my_context.getWrappedField("folder_image").tag(my_context, scale='icon', css_class = 'folder_image')
			self.folder_image_listing = my_context.getWrappedField("folder_image").tag(my_context, scale='listing', css_class = 'folder_image')
			self.folder_image_full = my_context.getWrappedField("folder_image").tag(my_context, scale='full', css_class = 'folder_image')
			self.folder_image_half = my_context.getWrappedField("folder_image").tag(my_context, scale='half', css_class = 'folder_image')
			self.folder_image_third = my_context.getWrappedField("folder_image").tag(my_context, scale='third', css_class = 'folder_image')
			self.folder_image_quarter = my_context.getWrappedField("folder_image").tag(my_context, scale='quarter', css_class = 'folder_image')
			
		except:
			self.folder_image = None
			self.folder_image_large = None
			self.folder_image_preview = None
			self.folder_image_mini = None
			self.folder_image_thumb = None
			self.folder_image_tile = None
			self.folder_image_icon = None
			self.folder_image_listing = None
			self.folder_image_full = None
			self.folder_image_half = None
			self.folder_image_third = None
			self.folder_image_quarter = None
		

	
class FolderTextViewlet(ViewletBase):
	render = ViewPageTemplateFile('folder_text.pt')

	def update(self):

		# Define self.folder_text

		# Acquisition.aq_base strips the acquisition layer from an object.
		# See: https://weblion.psu.edu/trac/weblion/wiki/OverridingPloneAcquisition
		my_context = aq_base(self.context)

		try:
			self.folder_text = my_context.folder_text
		except:
			self.folder_text = None

