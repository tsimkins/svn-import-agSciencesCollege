from archetypes.schemaextender.field import ExtensionField
from archetypes.schemaextender.interfaces import ISchemaExtender
from Products.Archetypes.atapi import *
from Products.ATContentTypes.interface.folder import IATFolder
from zope.interface import implements
from zope.component import adapts
from Products.ATContentTypes.configuration import zconf
#from Products.validation.validators.SupplValidators import MaxSizeValidator

#validation.register(MaxSizeValidator('checkImageMaxSize',
#                                     maxsize=zconf.ATImage.max_file_size))

#                max_size = zconf.ATImage.max_image_dimension,  

# Any field you tack on must have ExtensionField as its first subclass:
class _ImageExtensionField(ExtensionField, ImageField):
    pass

class _TextExtensionField(ExtensionField, TextField):
    pass

class FolderTextAndImage(object):
    """Adapter that adds an image to Folder."""
    adapts(IATFolder)
    implements(ISchemaExtender)
    
    _fields = [
            _ImageExtensionField('folder_image',
                required=False,
                widget=ImageWidget(
            		label="Folder Image",
            		label_msgid='Folder_label_image',
            		i18n_domain='Folder',
            		description="Image for folder from extender",
        		),
                storage=AttributeStorage(),
                swallowResizeExceptions = zconf.swallowImageResizeExceptions.enable,
                pil_quality = zconf.pil_config.quality,
                pil_resize_algo = zconf.pil_config.resize_algo,   
    			original_size=(300,300),
                sizes= {
                   'large'   : (768, 768), 
                   'preview' : (400, 400),
                   'mini'    : (200, 200),
                   'thumb'   : (128, 128),
                   'tile'    :  (64, 64),
                   'icon'    :  (32, 32),
                   'listing' :  (16, 16),
                   'full' :  (500, 500),
                   'half' :  (300, 300),
                   'third' :  (200, 200),
                   'quarter' :  (150, 150),
                  },

            ),
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
