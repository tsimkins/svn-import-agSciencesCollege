# This script will trawl through all the Plone sites at the root level of the site, and 
# update the base_properties file to contain any new base_properties
#

rules_path = "portal_cache_settings/with-caching-proxy/rules"
headerset_path = "portal_cache_settings/with-caching-proxy/headersets"

master_cache_site = 'agsci.psu.edu'

master_site = getattr(context, master_cache_site)

master_rules_folder = master_site
master_headerset_folder = master_site

for part in rules_path.split("/"):
	master_rules_folder = getattr(master_rules_folder, part)

for part in headerset_path.split("/"):
	master_headerset_folder = getattr(master_headerset_folder, part)
	 

for myKey in context.keys():
	
	if myKey == master_cache_site:
		continue
	
	myChild = getattr(context, myKey)
	
	try:
		myPortalType = myChild.getPortalTypeName()
	except:
		#print "No getPortalTypeName"
		pass
	else:
	
		if myPortalType == 'Plone Site':
			# Let's give it a go!

			local_rules_folder = myChild
			local_headerset_folder = myChild
			
			try:
				for part in rules_path.split("/"):
					local_rules_folder = getattr(local_rules_folder, part)
					
			except AttributeError:
				#print "Couldn't find %s for %s" % (rules_path, id)
				local_rules_folder = None
				pass

			try:	
				for part in headerset_path.split("/"):
					local_headerset_folder = getattr(local_headerset_folder, part)

			except AttributeError:
				#print "Couldn't find %s for %s" % (headerset_path, id)
				local_headerset_folder = None
				pass
			
			if local_rules_folder and local_headerset_folder:
				print "="*80
				print "Updating %s" % (myChild['id'])
				print "="*80				
				
				print local_rules_folder
				print local_headerset_folder
				
				print "-"*80
				print "Updating Rules"
				print "-"*80
								
				for masterKey in master_rules_folder.keys():
					if local_rules_folder.get(masterKey):
						print "Deleting %s in local" % masterKey
						local_rules_folder.manage_delObjects([masterKey])

					print "Copying %s from master" % masterKey
					myClipboard = master_rules_folder.manage_copyObjects(ids=[masterKey])
					local_rules_folder.manage_pasteObjects(cb_copy_data=myClipboard)

				print "-"*80
				print "Updating Headersets"
				print "-"*80

				for masterKey in master_headerset_folder.keys():
					if local_headerset_folder.get(masterKey):
						print "Deleting %s" % masterKey
						local_headerset_folder.manage_delObjects([masterKey])

					print "Copying %s from master" % masterKey
					myClipboard = master_headerset_folder.manage_copyObjects(ids=[masterKey])
					local_headerset_folder.manage_pasteObjects(cb_copy_data=myClipboard)

				print
				print
		
return printed

