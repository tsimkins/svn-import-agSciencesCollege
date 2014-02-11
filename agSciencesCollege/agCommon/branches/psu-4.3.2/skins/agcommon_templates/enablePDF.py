from Products.agCommon import enablePDF

request = container.REQUEST
response =  request.response

enabled = enablePDF(context)

if enabled:
    return context.REQUEST.RESPONSE.redirect("%s/edit" % context.absolute_url())
else:
    print """<p>PDF behavior already enabled for <a href="%s">%s</a>.</p>""" % (context.absolute_url(), context.Title().strip())
    print "<p>Options:</p><ul>"
    print """<li><a href="%s/edit">Edit Document</a></li>""" % context.absolute_url()
    print """<li><a href="%s/manage_interfaces">Remove</a> (Uncheck <strong>IUniversalPublicationExtender</strong>)</li>""" % context.absolute_url()
    print "</ul>"
    return printed


