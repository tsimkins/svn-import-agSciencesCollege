from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.app.layout.viewlets.common import ViewletBase
from zope.component import getMultiAdapter
from Products.Archetypes.BaseObject import BaseObject
from Acquisition import aq_base

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

