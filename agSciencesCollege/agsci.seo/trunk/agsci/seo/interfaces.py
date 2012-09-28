from zope.interface import Interface
from plone.theme.interfaces import IDefaultPloneLayer

class ISEOLayer(IDefaultPloneLayer):
    """A Layer Specific to agsci.seo"""

class ICanonicalURLExtender(Interface):
    """For things that need a canonical URL"""
