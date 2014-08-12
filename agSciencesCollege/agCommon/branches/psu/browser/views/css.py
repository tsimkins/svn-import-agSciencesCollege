from Products.Five import BrowserView
from Products.agCommon import getPanoramaHomepageImage
from zope.interface import implements, Interface

class ICSSView(Interface):
    pass

class CSSView(BrowserView):

    implements(ICSSView)

    def __init__(self, context, request):
        self.context = context
        self.request = request

class TileHomepage(CSSView):
    
    total_width = 908.0
    padding = 15.0
    max_blocks = 5
    max_items = 5

    def getBlockWidths(self, min_width=0):

        widths = []

        for i in range(1,self.max_blocks+1):
            for j in range(1,i+1):
                w = ((100.0*j)/i)
                if w >= min_width:
                    widths.append(w)
        
        return [('%d' % x, '%0.6f' % x, x/100) for x in sorted(list(set(widths)))]

    def getRSSImageCSS(self):

        css = []

        for (block_klass, block_css, block_percent) in self.getBlockWidths(min_width=50):
            css.append("""
        
                #portlets-above .portlet-width-%(block_klass)s.portlet-item-count-1 .rssImage{
                    width: 33%%;
                    float: right;
                    margin: 0 0 0.125em 0.25em;
                    padding: 0;
                }

            """ % {
                    'block_klass' : block_klass, 
                    })

        return css

    def getBlockCSS(self, mq=None):

        css = []

        for (block_klass, block_css, block_percent) in self.getBlockWidths():
        
            block_width = block_percent*self.total_width
            
            if mq in ('SMALLPHONE', 'BIGPHONE'):
                block_width = self.total_width
                block_css = '100'
                block_percent = 1
            
            header_width = block_width - (2*self.padding)
            header_width_percent = header_width/block_width
            header_padding_percent = self.padding/block_width            
        
            css.append("""
        
                #portlets-above .portlet-width-%(block_klass)s {
                    width: %(block_css)s%%;
                    float: left;
                    padding: 0;
                    margin: 0.5em 0 0 0;
                }
                
                #portlets-above .portlet-width-%(block_klass)s .portletHeader,
                #portlets-above .portlet-width-%(block_klass)s .portletFooter {
                    display: block;
                    width: %(header_width_percent)0.6f%%;
                    margin: 0 %(header_padding_percent)0.6f%%;
                    padding: 2em 0 0.25em 0;
                }
                
                #portlets-above .portlet-width-%(block_klass)s .portletFooter {
                    padding: 0.25em 0 0 0;
                    clear: both;
                }

            """ % {
                    'block_klass' : block_klass, 
                    'block_css' : block_css, 
                    'header_width_percent' : 100*header_width_percent,
                    'header_padding_percent' : 100*header_padding_percent,
                    })
            
            for n in range(1,self.max_items+1):
                css.extend(self.getItemCSS(n, block_percent, block_klass, mq=mq))

        return css

    def getItemCSS(self, n, block_percent, block_klass, mq=''):
        column_count = n

        if mq in ('TABLET'):
            if n > 2:
                column_count = 2
        elif mq in ('BIGPHONE', 'SMALLPHONE'):
            column_count = 1
            
        css = []
        
        block_width = block_percent*self.total_width
        total_padding = 2*column_count*self.padding
        content_width = (block_width - total_padding)/column_count
        content_width_percent = content_width/block_width
        padding_percent = self.padding/block_width

        css.append("    /* Block width % d, Content width: %d */" % (block_width, content_width))

        css.append("""
            #portlets-above .portlet-width-%(block_klass)s.portlet-item-count-%(n)s .portletItem {
                width: %(content_width_percent)0.6f%%;
                margin: 0.375em %(padding_percent)0.6f%% 1em %(padding_percent)0.6f%%;
                float: left;
            }
            
            #portlets-above .portlet-width-%(block_klass)s.portlet-item-count-%(n)s .portletItem:nth-child(%(n_child)sn + 1) {
                clear: left;
            }
        """ % {'block_klass' : block_klass, 'n' : n, 'content_width_percent' : content_width_percent*100, 'padding_percent' : padding_percent*100, 'n_child' : column_count})
        
        return css

    
    def getContentWellPortletCSS(self):
    
        homepage_text_width = (self.total_width - 2*self.padding)/self.total_width
        homepage_text_padding = self.padding/self.total_width
    
        return ["""

        #portlets-above {
            display: block;
        }

        div.AbovePortletManager1, 
        div.AbovePortletManager2, 
        div.AbovePortletManager3, 
        div.AbovePortletManager4, 
        div.AbovePortletManager5 {
            float: none;
            clear: both;
            width: 100%%;
            margin: 0;
            padding: 0;
        }

        #portlets-above .portletHeader {
            display: block !important;
            font-size: 1em;
            font-weight: bold;
            text-transform: none;
            padding-bottom: 0 !important;
            border-bottom: 1px solid #4B4B4B;
            color: #4B4B4B;
            font-family: Arial,Helvetica,Helv,sans-serif;
        }

        #portlets-above .portletItem a, 
        #portlets-above .portletItem .state-published {
            color: #2256BD !important;
            display: block;
            padding: 0 !important;
            font-size: 0.90625em;
        }

        #portlets-above .portletItem a:hover, 
        #portlets-above .portletItem .state-published:hover {
            text-decoration: underline;
            background-color: transparent !important;
            color: #2256BD !important;
            border-bottom: none;
        }
        
        #portlets-above .portletItem .portletItemDetails,
        #portlets-above .portletFooter a {
            color: #575757;
            font-weight: normal;
            font-size: 0.75em;
            line-height: 1.5em;
        }

        #portlets-above .portletItem .portletItemDetails.date,
        #portlets-above .portletItem .portletItemDetails.location {
            font-size: 0.6875em;
            color: #767676;
        }

        #portlets-above .rssImage {
            margin-bottom: 0.125em;
        }

        #portlets-above .portletFooter {
        }

        
        #portlets-above .portletFooter a {
            color: #2256BD;
        }

        #portlets-above .portletFooter a:hover {
            text-decoration: underline;
        }
        
        #content #homepage-text {
            width: %(homepage_text_width)0.6f%%;
            padding: 0.375em %(homepage_text_padding)0.6f%%;
            margin: 0;
        }

        """ % {'homepage_text_width' : 100*homepage_text_width, 'homepage_text_padding' : 100*homepage_text_padding}]

    def getPortletCSS(self):
        return ["""

        #portlets-above .portlet {
            margin-bottom: 1em;
        }
        
        #portlets-above .portlet img {
            max-width: 100%;
            width: 100%;
            height: auto;
        }
        
        """]

    def getMediaQuery(self, max_width=None, min_width=None):
        if max_width and min_width:
            return """
                @media handheld, screen and (max-width: %dpx) and (min-width: %dpx) {
                    %%s
                }
            """ % (max_width, min_width)
        elif max_width:
            return """
                @media handheld, screen and (max-width: %dpx) {
                    %%s
                }
            """ % (max_width)
        elif min_width:
            return """
                @media handheld, screen and (min-width: %dpx) {
                    %%s
                }
            """ % (min_width)
        else:
            return '%s'

    def __call__(self):

        RESPONSE =  self.request.RESPONSE
        RESPONSE.setHeader('Content-Type', 'text/css')
        RESPONSE.setHeader('Cache-Control', 'max-age=3600, s-maxage=3600, public, must-revalidate, proxy-revalidate')
        
        css = []
        css.extend(self.getPortletCSS())
        css.extend(self.getContentWellPortletCSS())
        css.extend(self.getRSSImageCSS())

        mq_list = [
                ('DESKTOP', self.getMediaQuery(min_width=769)),
                ('TABLET', self.getMediaQuery(max_width=768)),
                ('BIGPHONE', self.getMediaQuery(max_width=520)),
                ('SMALLPHONE', self.getMediaQuery(max_width=480)),
        ]
        
        for (mq, mq_format) in mq_list:
            css.append(mq_format % "\n".join(self.getBlockCSS(mq=mq)))
                        
        return """
        /* So, you'd like some CSS, eh? */
        %s
        """ % "\n".join(css)