from Products.agCommon import gradientBackground

request = container.REQUEST
RESPONSE =  request.RESPONSE

RESPONSE.setHeader('Content-Type', 'image/png')
print gradientBackground(request)

return printed
