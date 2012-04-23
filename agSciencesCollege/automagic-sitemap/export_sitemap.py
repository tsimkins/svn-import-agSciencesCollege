"""
Automagic Sitemap Generator
---------------------------
Requirements:

  * Plone
  * XCode (to get AppleScript Editor)
  * Omnigraffle (Tested on version 4)

This script queries the catalog for the types in the `portal_types` list, and 
excludes items with the ids in the `exclude` list.  It then creates a psuedo-URL
sitemap (using the title of the object in place of the URL) for use as input
into the create_sitemap Applescript.

To use, create a Python Script in your site root (or ZMI root) and paste this in.

Then, run this from  `http://mysite.psu.edu/export_sitemap.py` and paste the source
(should contain <loc> tags) into an XML file.  Or, use `curl` to download the URL, 
which is even easier!  Regardless, save this file as `mysite.xml`.  Unless you 
specifically want all (public and private) objects, it's best to do this from the
logged out http:// URL.

Then open the AppleScript Editor.  Make a new script.  Paste the 
`create_sitemap.applescript` into the script editor.  Save As with File Format 
of 'Application'.

In Finder, drag your `mysite.xml` file onto the AppleScript droplet.  Omnigraffle
will open and chug through the sitemap creation.  This may take awhile (5-15 minutes.)

For large sites, you will need to manually re-do the layout.

Bugs:  Draws multiple connector lines for items with multiple child objects.

"""

from Products.CMFCore.utils import getToolByName
portal_catalog = getToolByName(context, "portal_catalog")

data = { context.id : context.Title() }
virtual_dict = {}
virtual = []

# id's to exclude
exclude = ['default', 'listing', 'recent', 'latest', 'front-page', 'upcoming', 
           'images', 'photos', 'files', 'pdf', 'background-images', 'sample']

# add "year" folders
exclude.extend([str(x) for x in range(1990,2025)])

# types to include
portal_types = ['Document', 'FSDFacultyStaffDirectory', 'Folder', 'FormFolder', 'Large Plone Folder', 
                'PhotoFolder',  'Topic', 'Blog', 'Subsite', 'Section']

results = portal_catalog.searchResults({'portal_type' : portal_types})

for r in results:
    url = r.getURL().replace(context.absolute_url(), context.id)
    title = r.Title.replace('/', ' - ')
    data[url] = title

for k in data.keys():
    parts = k.split("/")
    if parts[-1] in exclude:
        parts.pop()
    title_parts = []
    for i in range(0, len(parts)):
        p = "/".join(parts[0:i+1])
        t = data.get(p, ('[%s]' % p).replace('/', '|'))
        title_parts.append(t)
    if len(title_parts) > 1 and title_parts[-1] == title_parts[-2]:
        title_parts.pop()
    title_parts = title_parts[0:6]
    virtual_title = "/".join(title_parts)
    virtual_dict[virtual_title] = 1

virtual = virtual_dict.keys()
virtual.sort()
for v in virtual:
    print "<loc>%s</loc>" % v
return printed
