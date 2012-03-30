from plone.app.portlets.portlets.rss import Renderer
from BeautifulSoup import BeautifulSoup
from urllib2 import urlopen
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.memoize.view import memoize

class RSSRenderer(Renderer):

    render_full = _template = ViewPageTemplateFile('templates/rss.pt')

    @memoize
    def item_image(self, url):
        if 'live.psu.edu' in url:
            soup = BeautifulSoup(urlopen(url))
            img = soup.find('img', {'id' : 'article_image'})

            if img:
                return """<img src="%s" alt="%s" />""" % (img['src'], 
img['alt'])

        return None

