from AccessControl import ClassSecurityInfo
from StringIO import StringIO
import csv
from Products.CMFCore import permissions
from zope.interface import implements, Interface
from Products.Five import BrowserView
from Products.CMFCore.utils import getToolByName
from DateTime import DateTime

class IRegistrationView(Interface):

    def getEventByUID(self):
        pass
        
    def canEditEvent(self, event):
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
    
    def canEditEvent(self, event):
        mt = getToolByName(self.context, 'portal_membership')
        return mt.checkPermission('cmf.ModifyPortalContent', event)
    
    def allowRegistration(self, event):
        if hasattr(event, 'free_registration_deadline'):
            registration_deadline = getattr(event, 'free_registration_deadline')
            if registration_deadline:
                if registration_deadline < DateTime():
                    return False
        return True
        

class DownloadCSVView(RegistrationView):
    security = ClassSecurityInfo()
    security.declareProtected(permissions.ModifyPortalContent, '__call__')

    def __call__(self):
        r_form = self.context.restrictedTraverse('register')
        save_data = r_form['save-data']
        out = StringIO()
        writer = csv.writer(out)
        event = self.getEventByUID()
        
        if event and self.canEditEvent(event) and save_data:
            filename = "%s.csv" % event.getId()
            titles = save_data.getColumnTitles()
            titles.pop(0)
            writer.writerow(titles)
            for r in save_data.getSavedFormInput():
                data_uid = r.pop(0)
                if data_uid == event.UID():
                    writer.writerow(r)
        else:
           filename = "error.csv"
           writer.writerow(["Error retrieving registration information. Either event does not exist, or you do not have the appropriate permissions."])
    
        self.request.response.setHeader('Content-Type', 'text/csv')
        self.request.response.setHeader('Content-Disposition', 'attachment; filename="%s"' % filename)
        

        return out.getvalue()