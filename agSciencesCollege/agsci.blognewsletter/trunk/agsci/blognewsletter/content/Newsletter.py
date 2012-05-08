from AccessControl import ClassSecurityInfo
from Products.Archetypes.atapi import *
from zope.interface import implements

from Products.ATContentTypes.content.topic import ATTopic
from Products.ATContentTypes.content.schemata import ATContentTypeSchema, finalizeATCTSchema

from agsci.blognewsletter.content.interfaces import INewsletter
from agsci.blognewsletter.config import *

from Products.Archetypes.public import StringField, StringWidget, BooleanField

Newsletter_schema = getattr(ATTopic, 'schema', Schema(())).copy()  +  Schema((

    StringField(
        "newsletter_title",
        required=False,
        schemata="settings",
        widget=StringWidget(
            label=u"Newsletter title",
            description=u"This will override the automatically generated title of the newsletter.",
            condition="python:member.has_role('Manager')",
        ),
    ),

    BooleanField(
        "show_print_newsletter",
        required=False,
        default=False,
        schemata="settings",
        widget=BooleanWidget(
            label=u"Show 'Print this newsletter' link",
            description=u"",
            condition="python:member.has_role('Manager')",
        ),
    ),
    
    BooleanField(
        "show_date",
        required=False,
        default=False,
        schemata="settings",
        widget=BooleanWidget(
            label=u"Show dates per-article",
            description=u"",
            condition="python:member.has_role('Manager')",
        ),
    ),

))


finalizeATCTSchema(Newsletter_schema, folderish=False)

class Newsletter(ATTopic):
    """
    """
    security = ClassSecurityInfo()
    implements(INewsletter)
    
    portal_type = 'Newsletter'
    _at_rename_after_creation = True
    
    schema = Newsletter_schema

    def getParentCriteria(self):

        # Grab parent node criteria.  Default to 'latest' collection if exists, 
        # otherwise grab default page.  Otherwise grab first collection in folder
        # listing.
        
        parent = self.getParentNode()
        default_page_id = self.getParentNode().getDefaultPage()
        topics = ['latest', default_page_id]
        
        for t in topics:
            if t in parent.objectIds() and parent[t].portal_type == 'Topic':
                return parent[t].listCriteria()
                
        topics_in_folder = parent.listFolderContents({'portal_type' : 'Topic'})

        if topics_in_folder:
            return topics_in_folder[0].listCriteria()
        else:
            return []
            
    def buildQuery(self):
        """Construct a catalog query using our criterion objects.
        """
        result = {}
        clear_start = False
        criteria = self.getParentCriteria()
        criteria.extend(self.listCriteria())
        
        acquire = self.getAcquireCriteria()
    
        if not criteria and not acquire:
            # no criteria found
            return None       

        if acquire:
            try:
                # Tracker 290 asks to allow combinations, like this:      
                # parent = aq_parent(self)
                clear_start = True
                parent = aq_parent(aq_inner(self))
                result.update(parent.buildQuery())
            except (AttributeError, Unauthorized): # oh well, can't find parent, or it isn't a Topic.
                pass

        for criterion in criteria:
            for key, value in criterion.getCriteriaItems():
                # Ticket: https://dev.plone.org/plone/ticket/8827
                # If a sub topic is set to acquire then the 'start' key have to
                # be deleted to get ATFriendlyDateCriteria to work properly (the 'end' key) -
                # so the 'start' key should be deleted.    
                # But only when:
                # - a subtopic with acquire enabled
                # - its a ATFriendlyDateCriteria
                # - the date criteria is set to 'now' (0)
                # - the end key is set
                if clear_start and criterion.meta_type in ['ATFriendlyDateCriteria'] \
                and not criterion.value and key == 'end' and 'start' in result:
                    del result['start']
                result[key] = value
        return result

    

registerType(Newsletter, PROJECTNAME)
