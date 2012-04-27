from Products.CMFPlone.interfaces import IPloneSiteRoot
from zope.schema.vocabulary import SimpleVocabulary
from zope.component import getUtility
from zope.schema.vocabulary import SimpleTerm
from zope.i18n import translate

from collective.contentleadimage.leadimageprefs import ILeadImagePrefsForm
from collective.contentleadimage import config
from collective.contentleadimage import LeadImageMessageFactory as _

class ScalesVocabulary(object):
    """ """

    def __call__(self, context):
        portal = getUtility(IPloneSiteRoot)
        cli_prefs = ILeadImagePrefsForm(portal)
        width = cli_prefs.image_width
        height = cli_prefs.image_height
        scale = config.IMAGE_SCALE_NAME
        result = [SimpleTerm(scale, scale, "%s (%dx%d)" % (scale, width, height)), ]
        
        for scale, (width, height) in config.IMAGE_SIZES.items():
            result.append( SimpleTerm(scale, scale, "%s (%dx%d)" % (scale, width, height)) )
            
        return SimpleVocabulary(result)
