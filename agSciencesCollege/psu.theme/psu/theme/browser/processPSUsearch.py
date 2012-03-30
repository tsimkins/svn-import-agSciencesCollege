from urllib import quote_plus

from zope.interface import Interface, implements
from Products.Five.browser import BrowserView


class IprocessPSUsearch(Interface):
    """This is what fancy people call a marker interface."""

_googleSearchQuery = 'http://google.com/search?q=%s'
    
_redirects = {
        'thisSite': 'search?SearchableText=%s',
        'google': _googleSearchQuery,
        'PSUweb': 'http://search-results.aset.psu.edu/search?q=%s&btnG=Search+Penn+State&client=PennState&proxystylesheet=PennState&output=xml_no_dtd&site=PennState',
        'PSUpeople': 'http://www.psu.edu/cgi-bin/ldap/ldap_query.cgi?cn=%s',
        'PSUemail': 'http://www.psu.edu/cgi-bin/ldap/ldap_query.cgi?uid=%s',
        'PSUdept': 'http://www.psu.edu/cgi-bin/ldap/dept_query.cgi?dept_name=%s'
    }

class processPSUsearch(BrowserView):
    """I need to put a doctest in here sometime soon."""
    implements(IprocessPSUsearch)
    
    def __call__(self):
        """"""
        req = self.context.REQUEST
        return req.RESPONSE.redirect(_redirects.get(req['choice'], _googleSearchQuery) % quote_plus(req['searchString']))
