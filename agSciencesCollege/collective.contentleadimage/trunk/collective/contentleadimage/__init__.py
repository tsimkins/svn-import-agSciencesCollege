from Products.validation.config import validation
from Products.validation.interfaces.IValidator import IValidator
from zope.i18n import MessageFactory
from zope.interface import implements

LeadImageMessageFactory = MessageFactory('collective.contentleadimage')

# import utils to register indexable attribute
import utils

def initialize(context):
    """Initializer called when used as a Zope 2 product."""

class ImageFormatValidator:
    implements(IValidator,)
    def __init__(self, name):
        self.name = name
    def __call__(self, value, *args, **kwargs):
        content_type = value.headers.get('content-type', '')
        if content_type not in ('image/jpeg', 'image/png', 'image/gif'):
            return "Image should be a web-friendly format, such as JPG, PNG, or GIF"
        return 1

validation.register(ImageFormatValidator('isValidImage'))
