from plonetheme.sunburst.browser.interfaces import IThemeSpecific as IThemeSunburst
from zope.interface import Interface

class IThemeSpecific(IThemeSunburst):
    """Marker interface"""

class IPhotoGalleryView(Interface):
    """
    photogallery view interface
    """

    def test():
        """ test method"""