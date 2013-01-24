from zope.interface import implements, Interface
from Products.agCommon.browser.views import FolderView
from Products.CMFCore.utils import getToolByName

class ICanonicalRedirectView(Interface):
    pass


class CanonicalRedirectView(FolderView):
    """
    Redirects entity to the corresponding content based on canonical URL
    """

    implements(ICanonicalRedirectView)


    def __call__(self):
        context = self.context
        mtool = getToolByName(context, 'portal_membership')
        can_edit = mtool.checkPermission('Modify portal content', context)
        
        redirectURL = None
        
        refs = self.context.getReferences(relationship = 'IsCanonicalURLFor')

        if refs:
            # Just in case it has multiples
            redirectURL = refs[0].absolute_url()

        elif hasattr(context, 'canonical_url_text') and getattr(context, 'canonical_url_text'):
            redirectURL = context.canonical_url_text
        
        if redirectURL and not can_edit:
            # Send to the configured website
            return context.REQUEST.RESPONSE.redirect(redirectURL)
        else:
            # Render the first layout listed
            layout = 'base_view'
            
            for (l,t) in context.getAvailableLayouts():
                if l != 'canonical_redirect':
                    layout = l
                    break
                                
            return eval("context.%s()" % layout)



