from plonetheme.classic.browser.interfaces import IThemeSpecific as IClassicTheme

class IThemeSpecific(IClassicTheme):
    """Marker interface"""

class ITagsView(Interface):
    """
    tags view interface
    """

    def test():
        """ test method"""
        
class INewsletterView(Interface):

    def test():
        """ test method"""