from Products.agCommon import bodyBackground
request = container.REQUEST
RESPONSE =  request.RESPONSE

RESPONSE.setHeader('Content-Type', 'image/png')

print bodyBackground(context, request)
return printed
