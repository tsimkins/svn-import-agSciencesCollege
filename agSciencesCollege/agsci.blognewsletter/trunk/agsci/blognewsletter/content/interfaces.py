from zope.interface import Interface

class IBlog(Interface):
    """Blogs are folders designed specifically for news items
    """
    
class INewsletter(Interface):
    """Newsletters are an email version of Blogs
    """
