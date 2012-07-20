from zope.i18nmessageid import MessageFactory
ExtensionExtenderMessageFactory = MessageFactory('agsci.ExtensionExtender')

from Products.CMFCore import DirectoryView

# Register our skins directory - this makes it available via portal_skins.

DirectoryView.registerDirectory('skins', globals())

def initialize(context):
    pass

