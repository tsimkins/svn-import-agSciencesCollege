from AccessControl import ClassSecurityInfo
from StringIO import StringIO
import csv
from Products.CMFCore import permissions
from zope.interface import implements, Interface
from Products.Five import BrowserView
from Products.CMFCore.utils import getToolByName
from DateTime import DateTime
from Products.agCommon import getContextConfig
from zope.app.component.hooks import getSite

class IRegistrationView(Interface):

    def getEventByUID(self):
        pass
        
    def canViewRegistrations(self, event):
        pass


class RegistrationView(BrowserView):

    implements(IRegistrationView)

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def getEventByUID(self):
        uid = self.request.form.get('uid')
        if uid:
            portal_catalog = getToolByName(self.context, "portal_catalog")
            results = portal_catalog.searchResults({'portal_type' : 'Event', 'UID' : uid})
            if results:
                r = results[0]
                o = r.getObject()
                return o
        return None

    def canViewRegistrations(self, event):
        mt = getToolByName(self.context, 'portal_membership')
        member = mt.getAuthenticatedMember()

        if member.has_role('Event Registration Viewer', event):
            return True
        elif mt.checkPermission('Modify portal content', event):
            return True
        else:
            return False
            
    def allowRegistration(self, event):
        if not event:
            return False

        now = DateTime()
        
        if now > event.end():
            return False
        
        if hasattr(event, 'free_registration_deadline'):
            registration_deadline = getattr(event, 'free_registration_deadline')
            if registration_deadline:
                if now > registration_deadline:
                    return False

        return True
    
    def registrationURL(self):
        url = getContextConfig(self.context, 'registration_url')

        if url:
            return url.replace('${portal_url}', '')
        else:
            return "%s/register" % getSite().absolute_url()
        

class DownloadCSVView(RegistrationView):
    security = ClassSecurityInfo()
    security.declareProtected(permissions.ModifyPortalContent, '__call__')

    def __call__(self):
        r_form = self.context.restrictedTraverse('register')
        save_data = r_form['save-data']
        out = StringIO()
        writer = csv.writer(out)
        event = self.getEventByUID()
        
        if event and self.canViewRegistrations(event) and save_data:
            filename = "%s.csv" % event.getId()

            titles = save_data.getColumnTitles()
            writer.writerow(titles[1:])
            for r in save_data.getSavedFormInput():
                data_uid = r[0]
                if data_uid == event.UID():
                    writer.writerow(r[1:])
        else:
           filename = "error.csv"
           writer.writerow(["Error retrieving registration information. Either event does not exist, or you do not have the appropriate permissions."])
    
        self.request.response.setHeader('Content-Type', 'text/csv')
        self.request.response.setHeader('Content-Disposition', 'attachment; filename="%s"' % filename)
        

        return out.getvalue()
