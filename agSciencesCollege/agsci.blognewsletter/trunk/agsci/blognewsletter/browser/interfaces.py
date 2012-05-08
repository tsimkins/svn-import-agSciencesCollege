from plonetheme.sunburst.browser.interfaces import IThemeSpecific as IThemeSunburst
from zope.interface import Interface

class IThemeSpecific(IThemeSunburst):
    """Marker interface"""

class ITagsView(Interface):
    """
    tags view interface
    """

    def test():
        """ test method"""
        
class INewsletterView(Interface):

    def getUTM(self):
        pass

    def test():
        """ test method"""