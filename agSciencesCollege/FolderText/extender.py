from archetypes.schemaextender.field import ExtensionField
from archetypes.schemaextender.interfaces import ISchemaExtender
from Products.Archetypes.atapi import *
from Products.ATContentTypes.interface.folder import IATFolder
from zope.interface import implements
from zope.component import adapts
from Products.ATContentTypes.configuration import zconf

# Any field you tack on must have ExtensionField as its first subclass:

class _TextExtensionField(ExtensionField, TextField):
    pass

class FolderText(object):
    """Adapter that adds text to Folder."""
    adapts(IATFolder)
    implements(ISchemaExtender)
    
    _fields = [
           _TextExtensionField('folder_text',
                required=False,
                widget=RichWidget(
                    label="Folder Text",
                    label_msgid='folder_label_text',
                    i18n_domain='Folder',
                    description="Text for folder from extender",
                ),
                default_output_type="text/x-html-safe",
                searchable=True,
                validators=('isTidyHtmlWithCleanup',)
            ),
        ]
    
    def __init__(self, folder):
        pass  # plop
        
    def getFields(self):
        return self._fields
