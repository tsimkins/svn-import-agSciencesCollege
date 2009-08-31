# This script will trawl through all the Plone sites at the root level of the site, and 
# compare the stock base_properties file with the customized version and show what's different.
#


for myKey in ['das.psu.edu']:
	
	myChild = getattr(context, myKey)
	
	try:
		if myChild.getPortalTypeName() == 'Plone Site':

			try:
				# Let's give it a go!
				print "Updating %s" % (myChild['id'])
				portal_skins = getattr(myChild, 'portal_skins')

				custom = getattr(portal_skins, 'custom')

				try:
					agcommon_styles = getattr(portal_skins, 'agcommon_styles')
				except:
					print "ERROR: %s : agCommon skin not installed" % myKey
					continue
					
				try:
					custom_base_properties = getattr(custom, 'base_properties')
				except:
					print "ERROR: %s : No customized base_properties" % myKey
					continue
					
				base_properties = getattr(agcommon_styles, 'base_properties')

				try:			
					for myProperty in custom_base_properties.propertyItems():
						(myPropertyKey, myPropertyValue) = myProperty
			
						myPropertyType = base_properties.getPropertyType(myPropertyKey)
								
						print "%s:%s=%s" % (myPropertyKey, myPropertyType, myPropertyValue)
				except:
					print "ERROR: %s : Problem updating properties" % myKey
			except:
				print "ERROR: %s : Some other error" % myKey
	except:
		# No portal type name
		# print "ERROR: %s : No Portal Type Name" % myKey
		pass				


		
return printed

