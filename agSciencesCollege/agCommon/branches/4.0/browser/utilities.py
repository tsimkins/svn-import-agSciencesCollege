import re
from zope.interface import implements, Interface
from Products.Five import BrowserView
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import normalizeString
from Acquisition import aq_acquire, aq_base
from urllib import urlencode
from Products.ZCatalog.CatalogBrains import AbstractCatalogBrain
from zope.component import getMultiAdapter

class IAgCommonUtilities(Interface):

    def substituteEventLocation(self):
        pass

    def reorderTopicContents(self):
        pass

    def toMarkdown(self):
        pass

    def getUTM(self):
        pass

    def customBodyClass(self):
        pass

class AgCommonUtilities(BrowserView):

    implements(IAgCommonUtilities)

    def substituteEventLocation(self, item):

        try:
            show_event_location = aq_acquire(self.context, 'show_event_location')
        except AttributeError:
            show_event_location = False
                
        if show_event_location and (item.portal_type == 'Event' or item.portal_type == 'TalkEvent'):
            if hasattr(item, 'short_location'):
                if isinstance(item, AbstractCatalogBrain):
                    if item.short_location:
                        return item.short_location
                elif item.short_location():
                    return item.short_location()
            elif item.location.strip():
                return item.location.strip()

        return None        
     
    def reorderTopicContents(self, topicContents, order_by_id=None, order_by_title=None):

        if order_by_id:

            def getId(item):
                if isinstance(item, AbstractCatalogBrain):
                    return item.getId
                else:
                    return item.getId()

            # The +1 applied to both outcomes is so that the index of 0 is not evaluated as false.
            return sorted(topicContents, key=lambda x: getId(x) in order_by_id and (order_by_id.index(getId(x)) + 1) or (len(order_by_id) + 1))
            
            # Reference code
            # The below is slightly faster than the above in cases where order_by_id <= ~5, but the above scales better.
            # I left it in as an explanation of what the above is doing.
            """
            ordered = []
            unordered = []
    
            # Grab all the unordered items
            for item in topicContents:
                if item.getId not in order_by_id:
                    unordered.append(item)
    
            # Grab the ordered items, in order
            for id in order_by_id:
                for item in topicContents:
                    if item.getId == id:
                        ordered.append(item)
    
            # Combine the two lists
            ordered.extend(unordered)
    
            return ordered
            """
        elif order_by_title:
            ordered = []
            uuids = {}

            def getConfig(item):
                if isinstance(item, AbstractCatalogBrain):
                    return item.UID
                else:
                    return item.UID()

            def getTitle(item):
                if isinstance(item, AbstractCatalogBrain):
                    return item.Title
                else:
                    return item.Title()

            for t in order_by_title:
                r = re.compile(t)
  
                # Pull out matching items
                for item in topicContents:
                    if not uuids.get(getConfig(item)) and r.search(getTitle(item)):
                        ordered.append(item)
                        uuids[getConfig(item)] = 1
  
            for item in topicContents:
                if not uuids.get(getConfig(item)):
                    ordered.append(item)
                    uuids[getConfig(item)] = 1

            return ordered
        else:
            return topicContents
        
    def toMarkdown(self, text):
        portal_transforms = getToolByName(self.context, 'portal_transforms')
        return portal_transforms.convert('markdown_to_html', text)
        
    def getUTM(self, source=None, medium=None, campaign=None, content=None):
        data = {}

        if source:
            data["utm_source"] = source

        if medium:
            data["utm_medium"] = medium

        if campaign:
            data["utm_campaign"] = campaign

        if content:
            data["utm_content"] = content

        return urlencode(data)

    def customBodyClass(self):
        context = aq_base(self.context)
        body_classes = []

        if hasattr(context, 'two_column') and context.two_column:
            body_classes.append('custom-two-column')

        try:
            if hasattr(context, 'folder_text'):
                body_text = str(context.folder_text)
            elif hasattr(context, 'getText'):
                body_text = str(context.getText())
            else:
                body_text = ''
        except:
            body_text = ''

        if body_text and '<h2' in body_text.lower() and '<h3' not in body_text.lower():
            body_classes.append('custom-h2-as-h3')

        # If 'show_mobile_nav' property is set or
        # we're the homepage at the root of the site, 
        # set class navigation-mobile
        
        try:
            # Explicitly enabled or is a homepage at the root of the site
            if getattr(self.context, 'show_mobile_nav', False) or (self.context.portal_type == 'HomePage' and self.context.getParentNode().portal_type == 'Plone Site'):
                body_classes.append("navigation-mobile")
        except:
            pass

        # If we have a property of 'enable_subsite_nav' set on
        # ourself, or if we're the default page and have it set on our parent
        # object, add a class of 'navigation-subsite'
        parent = self.context.getParentNode()

        try:
            parent_default = parent.getDefaultPage()
        except AttributeError:
            parent_default = ''

        try:
            # Explicitly enabled or is a homepage at the root of the site
            if context.getProperty('enable_subsite_nav', False) or self.context.getId() == parent_default and parent.getProperty('enable_subsite_nav', False):
                body_classes.append("navigation-subsite-root")
        except:
            pass

        try:
            enable_subsite_nav = aq_acquire(self.context, 'enable_subsite_nav')
            if enable_subsite_nav:
                body_classes.append("navigation-subsite")
        except AttributeError:
            pass

        try:
            penn_state_header = aq_acquire(self.context, 'main_site')
            if penn_state_header:
                body_classes.append("penn-state-header")
        except AttributeError:
            pass

        try:
            custom_class = aq_acquire(self.context, 'custom_class')
            body_classes.extend(['custom-%s' % str(x) for x in custom_class.split()])
        except AttributeError:
            pass
            
        # Set "empty-top-navigation" body class
        try:
            topMenu = aq_acquire(self.context, 'top-menu')
        except AttributeError:
            topMenu = 'topnavigation'

        portal_actions = getToolByName(self.context, 'portal_actions')

        if not portal_actions.get(topMenu, None):
            body_classes.append('empty-top-navigation')
        

        return ' '.join(body_classes)