from Acquisition import aq_base, aq_inner, aq_chain
from agsci.blognewsletter.content.interfaces import IBlog

def getAvailableTags(self):
    """Products.ATContentTypes.content.newsitem.ATNewsItem"""

    tags = []
    for i in aq_chain(self):
        if IBlog.providedBy(i):
            try:
                tags = i.available_public_tags
            except AttributeError:
                pass
            break
    return tags

