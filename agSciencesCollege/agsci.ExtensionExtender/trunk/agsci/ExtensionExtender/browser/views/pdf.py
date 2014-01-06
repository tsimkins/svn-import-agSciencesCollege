from zope.interface import implements, Interface
from Products.Five import BrowserView
from Products.CMFCore.utils import getToolByName
from Acquisition import aq_acquire, aq_inner
from collective.contentleadimage.config import IMAGE_FIELD_NAME, IMAGE_CAPTION_FIELD_NAME
from DateTime import DateTime
from urllib import urlencode
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from BeautifulSoup import BeautifulSoup, NavigableString, Tag
from zope.component import getUtility, getMultiAdapter
from collective.contentleadimage.leadimageprefs import ILeadImagePrefsForm
from Products.agCommon.browser.views import FolderView, IFolderView
from urlparse import urljoin
import re

from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, BaseDocTemplate, Frame, PageTemplate, FrameBreak
from reportlab.platypus.flowables import HRFlowable, KeepTogether, ImageAndFlowables, ParagraphAndImage
from reportlab.platypus.figures import ImageFigure as ImageFigureBase
from reportlab.platypus.figures import FlexFigure
from reportlab.platypus.tables import Table, TableStyle
from reportlab.platypus.tableofcontents import TableOfContents
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.utils import ImageReader
from reportlab.lib.colors import Color
from reportlab.rl_config import _FUZZ
from reportlab.lib.enums import TA_LEFT, TA_RIGHT, TA_CENTER

from io import BytesIO
from uuid import uuid4

from PIL import Image as PILImage

import os

from zope.app.component.hooks import getSite

from Products.CMFPlone.interfaces import IPloneSiteRoot

class ImageFigure(ImageFigureBase, Image):
    """Image with a caption below it"""
    def __init__(self, img_data, caption, width, height, background=None, align='right', max_image_width=None, column_count=1):
        self.img = PILImage.open(img_data)
        w, h = self.img.size

        if max_image_width > w:
            scaleFactor = max_image_width/w            
        else:
            scaleFactor = width/w            

        FlexFigure.__init__(self, w*scaleFactor, h*scaleFactor, caption, background)
        self.border=0
        self.captionFont='Helvetica'
        self.captionTextColor='gray'
        self.captionSize=9
        self.scaleFactor = self._scaleFactor = scaleFactor
        self.vAlign = 'TOP'
        self.hAlign = 'LEFT'
        self.column_count = column_count

    def drawFigure(self):
        (w,h) = self.img.size
        if self.column_count == 1:
            self.canv.drawInlineImage(self.img, x=-w*self.scaleFactor/2, y=0, width=w*self.scaleFactor, height=h*self.scaleFactor)
        else:
            self.canv.drawInlineImage(self.img, x=0, y=0, width=w*self.scaleFactor, height=h*self.scaleFactor)
            
    def drawCaption(self):
        (w,h) = self.img.size
        self.captionStyle.alignment = TA_LEFT

        if self.column_count == 1:
            self.captionPara.drawOn(self.canv, -w*self.scaleFactor/2, 0)  
        else:
            self.captionPara.drawOn(self.canv, 0, 0)  


    @property
    def drawWidth(self):
        return self.width

    @property
    def drawHeight(self):
        caption_height = self.captionPara.wrap(self.width, 100)[1] + self.captionGap
        return self.figureHeight + caption_height

    def _restrictSize(self,aW,aH):
        if self.drawWidth>aW+_FUZZ or self.drawHeight>aH+_FUZZ:   
            self._oldDrawSize = self.drawWidth, self.drawHeight 
            factor = min(float(aW)/self.drawWidth,float(aH)/self.drawHeight)
            self.drawWidth *= factor
            self.drawHeight *= factor
        return self.drawWidth, self.drawHeight

    def _unRestrictSize(self):
        dwh = getattr(self,'_oldDrawSize',None)
        if dwh:
            self.drawWidth, self.drawHeight = dwh




class FactsheetDocTemplate(BaseDocTemplate):
    def __init__(self, filename, **kw):
        BaseDocTemplate.__init__(self,filename, **kw)

    def afterFlowable(self, flowable):
        "Registers TOC entries."
        if flowable.__class__.__name__ == 'Paragraph':
            text = flowable.getPlainText()
            style = flowable.style.name
            unique_key = uuid4().hex
            self.canv.showOutline()
            self.canv.bookmarkPage(unique_key)
            if style == 'Heading1':
                self.canv.addOutlineEntry(text, unique_key, level=0, closed=None)
            elif style == 'Heading2':
                self.canv.addOutlineEntry(text, unique_key, level=1, closed=None)
            elif style == 'Heading3':
                self.canv.addOutlineEntry(text, unique_key, level=2, closed=None)

class FactsheetPDFView(FolderView):
    """
    View for downloading PDF version of factsheet
    """
    implements(IFolderView)

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.site = getSite()


    def __call__(self):
        # Use the publication code as the filename, if it exists.  Otherwise,
        # use the plone id

        filename = self.getPublicationCode()

        if not filename:
            filename = self.context.getId()

        pdf = self.createPDF() # Remove this line when done debugging

        try:
            #pdf = self.createPDF()
            pass
        except:
            # Also send email
            return "<h1>Error</h1><p>Sorry, an error has occurred.</p>"

        self.request.response.setHeader('Content-Type', 'application/pdf')
        self.request.response.setHeader('Content-Disposition', 'attachment; filename="%s.pdf"' % filename)

        return pdf

    def getPublicationCode(self):
        if hasattr(self.context, 'extension_publication_code') and self.context.extension_publication_code:
            return self.context.extension_publication_code.upper().strip()
        else:
            return ""


    def getPublicationSeries(self):
        if hasattr(self.context, 'extension_publication_series') and self.context.extension_publication_series:
            return self.context.extension_publication_series.strip()
        else:
            return ""

    def createPDF(self):

        # -------------------------------------------------------------------------
        # Define functions used internally
        # -------------------------------------------------------------------------

        # Returns the plain (non-HTML) text for an item.  Used at the lowest level
        # of the DOM tree because it doesn't preserve any HTML formatting

        def getItemText(item):
            if isinstance(item, Tag):
                return portal_transforms.convert('html_to_text', item.prettify()).getData()
            elif isinstance(item, NavigableString):
                return str(item).strip()
            else:
                return str(item).strip()


        # Provides the limited subset of HTML content used by the PDF generator

        def getInlineContents(item):
            p_contents = []
            for i in item.contents:
                if isinstance(i, Tag):
                    item_type = i.name
                    if item_type in ['b', 'strong', 'i', 'em', 'super', 'sub', 'a']:
                        for a in ['class', 'title', 'rel']:
                            if i.get(a):
                                del i[a]
                        if item_type == 'strong':
                            i.name = 'b'
                        elif item_type == 'em':
                            i.name = 'i'
                        elif item_type == 'a':
                            i.name = 'link'
                            if not (i['href'].startswith('http') or i['href'].startswith('mailto')):
                                i['href'] = urljoin(self.context.absolute_url(), i['href'])
                            # Wouldn't it be nice to underline the links?
                            i['color'] = 'blue'
                        if i.string:
                            p_contents.append(i.prettify())
                        else:
                            p_contents.append(getInlineContents(i))
                    else:
                        p_contents.append(getItemText(i))
                elif isinstance(i, NavigableString):
                    p_contents.append(str(i).strip())
            return "".join(p_contents)


        # Returns structure containing table data when passed a BeautifulSoup
        # <table> element.
        def getTableData(item):

            def getCellSpan(cell):
                colspan = int(cell.get('colspan', 1))
                rowspan  = int(cell.get('rowspan', 1))
                return (colspan, rowspan)

            th_bg = Color(0.8,0.8,0.8)
            th_text = Color(0,0,0)
            grid = Color(0.6,0.6,0.6)

            table_data = []
            table_style = []

            r_index = 0

            for tr in item.findAll('tr'):
                c_index = 0

                table_row = []

                for i in tr.findAll('th'):
                    table_row.append(getInlineContents(i))
                    (colspan, rowspan) = getCellSpan(i)
                    c_max = c_index + colspan - 1
                    r_max = r_index + rowspan - 1
                    table_style.extend([
                        ('FONTNAME', (c_index,r_index), (c_index,r_index), 'Times-Bold'),
                        ('FONTSIZE', (c_index,r_index), (c_index,r_index), 9),
                        ('BACKGROUND', (c_index,r_index), (c_index,r_index), th_bg),
                        ('GRID', (c_index,r_index), (c_max,r_max), 0.5, grid),
                        ('TEXTCOLOR', (c_index,r_index), (c_index,r_index), th_text),
                        ('LEFTPADDING', (c_index,r_index), (c_index,r_index), 3),
                        ('RIGHTPADDING', (c_index,r_index), (c_index,r_index), 3),
                        ('SPAN', (c_index,r_index), (c_max,r_max)),
                      ]
                    )
                    c_index = c_index + 1

                for i in tr.findAll('td'):
                    table_row.append(getInlineContents(i))
                    (colspan, rowspan) = getCellSpan(i)
                    c_max = c_index + colspan - 1
                    r_max = r_index + rowspan - 1
                    table_style.extend([
                        ('GRID', (c_index,r_index), (c_max,r_max), 0.5, grid),
                        ('FONTNAME', (c_index,r_index), (c_index,r_index), 'Times-Roman'),
                        ('FONTSIZE', (c_index,r_index), (c_index,r_index), 9),
                        ('LEFTPADDING', (c_index,r_index), (c_index,r_index), 3),
                        ('RIGHTPADDING', (c_index,r_index), (c_index,r_index), 3),
                        ('SPAN', (c_index,r_index), (c_max,r_max)),
                      ]
                    )
                    if i.get('align', '').lower() == 'right':
                        table_style.extend([
                            ('ALIGN', (c_index,r_index), (c_index,r_index), 'RIGHT'),
                          ]
                        )
                    c_index = c_index + 1

                table_data.append(table_row)
                r_index = r_index + 1

            caption = item.find('caption')

            return (table_data, TableStyle(table_style), caption)


        # Provides the PDF entities for the corresponding HTML tags.

        def getContent(item):
            pdf = []
            if isinstance(item, Tag):
                className=item.get('class', '').split()
                item_type = item.name
                if item_type in ['h2', 'h3', 'h4', 'h5', 'h6']:
                    item_style = tag_to_style.get(item_type)
                    h = Paragraph(getItemText(item), styles[item_style])
                    h.keepWithNext = True
                    pdf.append(h)
                elif item_type in ['table']:
                    (table_data, table_style, caption) = getTableData(item)
                    table = Table(table_data)
                    table.setStyle(table_style)
                    table.hAlign = 'LEFT'
                    if caption:
                        caption_el = Paragraph(getInlineContents(caption), discreet)
                        pdf.append(KeepTogether([table, caption_el]))
                    else:
                        pdf.append(table)
                elif item_type in ['ul']:
                    for i in item.findAll('li'):
                        pdf.append(Paragraph('<bullet>&bull;</bullet>%s' % getInlineContents(i), bullet_list))
                elif item_type in ['ol']:
                    for i in item.findAll('li'):
                        pdf.append(Paragraph('<seq />. %s' % getInlineContents(i), bullet_list))
                elif item_type in ['p'] or (item_type in ['div'] and 'captionedImage' in className):

                    has_image = False

                    # Pull images out of items and add before
                    for img in item.findAll('img'):
                        img.extract()
                        src = img['src'].replace(self.site.absolute_url(), '')

                        if src.startswith('/'):
                            src = src.replace('/', '', 1)
                            
                        try:
                            img_obj = self.site.restrictedTraverse(str(src))
                        except KeyError:
                            continue

                        has_image = True
                        pdf_image = getImage(img_obj)
                        pdf.append(pdf_image)

                    # If we had an image, and the next paragraph has the
                    # 'discreet' class (is a caption) then keep them together
                    if has_image:
                        s = item.findNextSiblings()
                        if s and 'discreet' in s[0].get('class', ''):
                            pdf[-1].keepWithNext = True

                    # Get paragraph contents
                    p_contents = getInlineContents(item)

                    # Don't add anything if no contents.
                    if not p_contents:
                        pass
                    elif 'discreet' in className or 'captionedImage' in className:
                        if len(pdf) and isinstance(pdf[-1], Image):
                            pdf[-1].keepWithNext = True
                        pdf.append(Paragraph(p_contents, discreet))
                    else:
                        pdf.append(Paragraph(p_contents, styles["Normal"]))

                elif item_type in ['div']:
                    for i in item.contents:
                        pdf.extend(getContent(i))

                elif item_type == 'blockquote':
                    pdf.append(Paragraph(getItemText(item), blockquote))
                else:
                    pdf.append(Paragraph(getItemText(item), styles["Normal"]))
            elif isinstance(item, NavigableString):
                if item.strip():
                    pdf.append(Paragraph(item, styles["Normal"]))
            return pdf

        # -------------------------------------------------------------------------
        # Main body of create PDF
        # -------------------------------------------------------------------------


        # Get document attributes

        title = self.context.Title()
        desc = self.context.Description()
        text = self.context.getText()


        # Determine whether or not to use long affirmative action statement
        use_long_statement = False

        if hasattr(self.context, 'extension_publication_long_statement') and self.context.extension_publication_long_statement:
            use_long_statement = True

        # Determine whether to push description into body text
        description_body = False

        if hasattr(self.context, 'extension_publication_description_body') and self.context.extension_publication_description_body:
            description_body = True

        # Number of columns
        column_count = 2

        if hasattr(self.context, 'extension_publication_column_count'):
            column_count = getattr(self.context, 'extension_publication_column_count', '2')

        try:
            column_count = int(column_count)
        except:
            column_count = 2

        # Grab the publication code
        publication_code = self.getPublicationCode()

        # Grab the publication series
        publication_series = self.getPublicationSeries()

        # Clean up text
        text = text.replace('&nbsp;', ' ')

        # Colors - Maybe have presets?
        #header_rgb = (0.42,0.56,0.07)
        header_rgb = (0.12,0.18,0.30)

        # Styles

        styles=getSampleStyleSheet()

        styles['Normal'].spaceBefore = 3
        styles['Normal'].spaceAfter = 6
        styles['Normal'].fontName = 'Times-Roman'

        styles['Heading1'].fontSize = 24
        styles['Heading1'].leading = 28
        styles['Heading1'].spaceAfter = 4

        styles['Heading2'].allowWidows = 0
        styles['Heading2'].fontSize = 13
        styles['Heading2'].textColor = header_rgb
        styles['Heading2'].leading = 15
        styles['Heading2'].spaceAfter = 4

        styles['Heading3'].allowWidows = 0
        styles['Heading3'].fontSize = 11
        styles['Heading3'].fontName = 'Helvetica'

        series_heading = ParagraphStyle('Series')
        series_heading.spaceBefore = 2
        series_heading.spaceAfter = 10
        series_heading.fontSize = 16
        series_heading.textColor = header_rgb

        bullet_list = ParagraphStyle('BulletList')
        bullet_list.spaceBefore = 4
        bullet_list.spaceAfter = 4
        bullet_list.fontName = 'Times-Roman'
        bullet_list.bulletIndent = 5
        bullet_list.leftIndent = 17
        bullet_list.bulletFontSize = 12

        blockquote = ParagraphStyle('Blockquote')
        blockquote.leftIndent = 12
        blockquote.rightIndent = 8
        blockquote.spaceAfter = 6
        blockquote.fontName = 'Times-Roman'

        discreet = ParagraphStyle('Discreet')
        discreet.fontSize = 9
        discreet.textColor = 'gray'
        discreet.spaceAfter = 8
        discreet.spaceBefore = 1

        statement = ParagraphStyle('Statement')
        statement.fontSize = 9
        statement.fontName = 'Times-Roman'
        statement.spaceAfter = 6

        description = ParagraphStyle('Description')
        description.fontSize = 16
        description.spaceAfter = 8
        description.leading = 20

        if description_body:
            description.fontSize = 11
            description.fontName = 'Helvetica-Bold'
            description.leading = 13

        padded_image = ParagraphStyle('PaddedImage')
        padded_image.spaceBefore = 12
        padded_image.spaceAfter = 12

        # Create document
        pdf_file = BytesIO()
        margin = 45

        doc = FactsheetDocTemplate(pdf_file,pagesize=letter, title=title,
                                   rightMargin=margin,leftMargin=margin, showBoundary=0,
                                   topMargin=margin,bottomMargin=margin)

        # Standard padding for document elements
        element_padding = 6
        
        # Document image setttings
        max_image_width = doc.width/column_count-(3*element_padding)
        
        if column_count <= 1:
            max_image_width = doc.width/2-(3*element_padding)

        # Returns a reportlab image object based on a Plone image object

        def getImage(img_obj, scale=True, reader=False, width=max_image_width, style="", column_count=column_count, caption="", leadImage=False, hAlign=None, body_image=True):

            if not leadImage and body_image and column_count == 1:
                # Special case to make one column body images 66% of the page
                width = 1.33*width

            img_width = img_obj.width
            img_height = img_obj.height

            if scale and (img_width > width):
                img_height = (width/img_width)*img_height
                img_width = width

            try:
                img_data = BytesIO(img_obj.data)
            except AttributeError:
                img_data = BytesIO(img_obj._data)

            if reader:
                img = ImageReader(img_data)
            else:
                if caption or leadImage:
                    img = ImageFigure(img_data, caption=caption, width=img_width, height=img_height, align="right", max_image_width=width, column_count=column_count)
                else:
                    img = Image(img_data, width=img_width, height=img_height)

            if style:
                img.style = style

            if hAlign:
                img.hAlign = hAlign
            elif column_count == 1:
                img.hAlign = TA_LEFT
            else:
                img.hAlign = TA_CENTER

            return img

        #-------------- calculated coordinates/w/h

        # Extension image header
        header_image_width = 175.0
        header_image_x = doc.leftMargin + (doc.width-(header_image_width))/2
        header_image_padding = 3*element_padding

        header_image = self.site.portal_skins.agcommon_images['penn-state-extension-word-mark-white.png']
        header_image_height = (header_image_width/header_image.width)*header_image.height

        extension_url_image = self.site.portal_skins.agcommon_images['extension-url.png']
        extension_url_image_width = 0.5*max_image_width

        outreach_image = self.site.portal_skins.agcommon_images['outreach-statement-long-black.png']

        # Colored background box
        header_bg_y = doc.height + header_image_height
        header_bg_height = header_image_height + header_image_padding

        header_image_y = header_bg_y + (header_image_padding/2)

        # Factsheet title 
        if publication_series:
            title_height = 99 # 1.375"
        else:
            title_height = 81 # 1.125"

        if desc.strip() and not description_body:
            title_height = title_height + 27  # 0.375"

        # Penn State/Extension Footer Image
        footer_image = self.site.portal_skins.agcommon_images['extension-factsheet-footer.png']
        footer_image_height = (doc.width/footer_image.width)*footer_image.height

        # Header and footer on first page
        def header_footer(canvas,doc):
            canvas.saveState()
            canvas.setStrokeColorRGB(*header_rgb)
            canvas.setFillColorRGB(*header_rgb)
            canvas.rect(doc.leftMargin, header_bg_y, doc.width, header_bg_height,fill=1)
            canvas.setStrokeColorRGB(0,0,0)

            # Background bounding box
            canvas.line(doc.leftMargin, doc.height+header_image_height-title_height-element_padding, doc.width+doc.leftMargin, doc.height+header_image_height-title_height-element_padding)

            # Extension logo
            canvas.drawImage(getImage(header_image, scale=False, reader=True), header_image_x, header_image_y, width=header_image_width, height=header_image_height, preserveAspectRatio=True, mask='auto')

            # Footer
            canvas.drawImage(getImage(footer_image, scale=False, reader=True), doc.leftMargin, doc.bottomMargin, width=doc.width, height=footer_image_height, preserveAspectRatio=True, mask='auto')

            canvas.restoreState()

        # Footer for pages 2 and after
        def footer(canvas,doc):
            canvas.saveState()
            canvas.setFont('Times-Roman',9)
            canvas.drawString(margin, 36, "Page %d" % doc.page)
            canvas.setFont('Times-Roman',9)
            canvas.drawRightString(doc.width+margin+element_padding, 36, title)
            canvas.restoreState()

        #Two Columns For First (title) page
        title_y = doc.height-title_height
        title_column_y = doc.bottomMargin+footer_image_height + 6
        title_column_height = title_y - title_column_y

        title_frame_title = Frame(doc.leftMargin, title_y, doc.width, title_height, id='title_title')

        title_frames = [title_frame_title]

        for i in range(0,column_count):
            lm = doc.leftMargin + i * (doc.width/column_count+element_padding)
            w = doc.width/column_count-element_padding
            title_frame = Frame(lm, title_column_y, w, title_column_height, id='title_col%d' % i)
            title_frames.append(title_frame)

        #Two Columns For remaining page

        other_frames = []

        for i in range(0,column_count):
            lm = doc.leftMargin + i * (doc.width/column_count+element_padding)
            w = doc.width/column_count-element_padding
            other_frame = Frame(lm, doc.bottomMargin, w, doc.height, id='other_col%d' % i)
            other_frames.append(other_frame)

        title_template = PageTemplate(id="title_template", frames=title_frames,onPage=header_footer)
        other_template = PageTemplate(id="other_template", frames=other_frames,onPage=footer)

        doc.addPageTemplates([title_template,other_template])
        doc.handle_nextPageTemplate("other_template")

        # ---------------------------------------------------------------------
        # Convert HTML to PDF (Magic goes here)
        # ---------------------------------------------------------------------

        # Soupify
        soup = BeautifulSoup(text)

        # This list holds the PDF elements
        pdf = []

        # Series, page heading and description in top frame, then framebreak
        # into two columns.  Optionally add the description to the body if the
        # flag is set.

        if publication_series:
            pdf.append(Paragraph(publication_series, series_heading))

        pdf.append(Paragraph(title, styles["Heading1"]))

        if description_body:
            pdf.append(FrameBreak())
            pdf.append(Paragraph(desc, description))
        else:
            pdf.append(Paragraph(desc, description))
            pdf.append(FrameBreak())

        # Lead Image and caption as first elements. Not doing News Item image.
        leadImage_field = self.context.getField(IMAGE_FIELD_NAME)
        leadImage_caption_field = self.context.getField(IMAGE_CAPTION_FIELD_NAME)

        if leadImage_field and leadImage_caption_field:
            leadImage = leadImage_field.get(self.context)
            leadImage_caption = leadImage_caption_field.get(self.context)

            if leadImage.get_size():
                if column_count == 1:
                    pdf.append(getImage(leadImage, caption=leadImage_caption, leadImage=True))

                else:
                    pdf.append(getImage(leadImage)) 

                    if leadImage_caption: 
                        pdf.append(Paragraph(leadImage_caption, discreet)) 


        # portal_transforms will let us convert HTML into plain text
        portal_transforms = getToolByName(self.context, 'portal_transforms')

        # Equivalent PDF paragraph styles for HTML
        tag_to_style = {
            'h2' : 'Heading2',
            'h3' : 'Heading3',
            'h4' : 'Heading4',
            'h5' : 'Heading5',
            'h6' : 'Heading6',
            'p' : 'Normal'
        }

        # Loop through Soup contents
        for item in soup.contents:
            pdf.extend(getContent(item))

        # Embed lead images in paragraphs if we're a single column
        if column_count == 1:
            for i in range(1,len(pdf)-1):
                if isinstance(pdf[i], ImageFigureBase):

                    paragraphs = []
                    
                    for j in range(i+1, len(pdf)-1):
                        if isinstance(pdf[j], Paragraph):
                            paragraphs.append(pdf[j])
                            pdf[j] = None
                        else:
                            break

                    if paragraphs:
    
                        pdf[i].hAlign="RIGHT"
                        
                        img_paragraph = ImageAndFlowables(pdf[i], paragraphs,imageLeftPadding=element_padding)
                        pdf[i] = img_paragraph

            while None in pdf:
                pdf.remove(None)

        # All done with contents, appending line and statement
        pdf.append(HRFlowable(width='100%', spaceBefore=4, spaceAfter=4))

        # Extension and Outreach logos

        pdf.append(getImage(extension_url_image, scale=True, width=extension_url_image_width, style=padded_image, hAlign='LEFT', body_image=False))
        pdf.append(getImage(outreach_image, style=padded_image, body_image=False))

        # Choose which statement
        if use_long_statement:
            aa_statement = """The Pennsylvania State University is committed to the policy that all persons shall have equal access to programs, facilities, admission, and employment without regard to personal characteristics not related to ability, performance, or qualifications as determined by University policy or by state or federal authorities. It is the policy of the University to maintain an academic and work environment free of discrimination, including harassment. The Pennsylvania State University prohibits discrimination and harassment against any person because of age, ancestry, color, disability or handicap, genetic information, national origin, race, religious creed, sex, sexual orientation, gender identity, or veteran status and retaliation due to the reporting of discrimination or harassment. Discrimination, harassment, or retaliation against faculty, staff, or students will not be tolerated at The Pennsylvania State University. Direct all inquiries regarding the nondiscrimination policy to the Affirmative Action Director, The Pennsylvania State University, 328 Boucke Building, University Park, PA 16802-5901; Tel 814-863-0471."""
        else:
            aa_statement = """Penn State is committed to affirmative action, equal opportunity, and the diversity of its workforce."""
        statement_text = ("""<b>Penn State College of Agricultural Sciences research and extension programs are funded in part by Pennsylvania counties, the Commonwealth of Pennsylvania, and the U.S. Department of Agriculture.</b>

        Where trade names appear, no discrimination is intended, and no endorsement by Penn State Cooperative Extension is implied.

        This publication is available in alternative media on request.

        %s

        &copy The Pennsylvania State University %d

        """ % (aa_statement, DateTime().year())).split("\n")

        # Append the publication code, if it exists
        if publication_code:
            statement_text.append("Publication code: %s" % publication_code)

        # Create paragraphs from the statement text
        for s in statement_text:
            if s.strip():
                pdf.append(Paragraph(s, statement))

        # Create PDF - multibuild instead of build for table of contents
        # functionality

        doc.multiBuild(pdf)
        #doc.build(pdf)

        # Pull PDF binary bits into variable, close file handle and return
        pdf_value = pdf_file.getvalue()
        pdf_file.close()
        return pdf_value