from zope.interface import Interface, Attribute

class ISubsite(Interface):
    """Subsites are folders designed specifically for subsites
    """

class ICountySite(Interface):
    """CountySites are folders designed specifically for Extension counties
    """

class ISection(Interface):
    """Sections are parts of a subsite with their own navigation
    """

class IBlog(Interface):
    """Blogs are folders designed specifically for news items
    """
    
class IHomePage(Interface):
    """Homepages are the home page of a site/section/subsite
    """

class INewsletter(Interface):
    """Homepages are the home page of a site/section/subsite
    """
    
class IPhotoFolder(Interface):
    """Photo Folders store images and present a slideshow display
    """
    
class ITagRoot(Interface):
    """Object implementing the ITagRoot interface have their own tagging
       subsystem.
    """