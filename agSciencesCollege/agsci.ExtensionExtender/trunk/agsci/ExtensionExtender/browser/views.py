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
import re

from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, BaseDocTemplate, Frame, PageTemplate, FrameBreak
from reportlab.platypus.flowables import HRFlowable, KeepTogether
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.utils import ImageReader
from cStringIO import StringIO
from io import BytesIO

from zope.app.component.hooks import getSite

from Products.CMFPlone.interfaces import IPloneSiteRoot

class ByCountyView(FolderView):
    """
    By County browser view
    """
    implements(IFolderView)
    
    def __init__(self, context, request):
        self.context = context
        self.request = request
        
        self.counties = []
        
        counties = {}

        results = []
        folder_path = ""
        
        self.here_url = self.context.absolute_url()
        
        if self.context.portal_type == 'Topic':
            try:
                results = self.context.queryCatalog()
            except AttributeError:
                # We don't like a relative path here for some reason.
                # Until we figure it out, fall through and just do the default query.
                # That should work in most cases.
                parent_physical_path = list(self.context.getPhysicalPath())
                parent_physical_path.pop()
                folder_path = '/'.join(parent_physical_path)
                pass
            
            # If we're a collection (Topic), we may be a default page  Figure out
            # if we're the default page, and if so, set the here_url to our parent.
            parent = self.context.getParentNode()
            if self.context.id == parent.getDefaultPage():
                self.here_url = parent.absolute_url()
            
        if not results:
            catalog = getToolByName(self.context, 'portal_catalog')
            
            if not folder_path:
                folder_path = '/'.join(self.context.getPhysicalPath())
             
            results = catalog.searchResults({'portal_type' : ['Event', 'TalkEvent', 'Person', 'News Item', 'Folder', 'Subsite', 'Section'],
                                            'path' : {'query': folder_path, 'depth' : 4} })
        for r in results:
        
            for county in r.extension_counties:
                
                if not counties.get(county):
                    counties[county] = {'id' : county.lower(), 
                                     'label' : county, 'items' : []}
    
                                    
                counties[county]['items'].append(r)

        for c in sorted(counties.keys()):
            self.counties.append(counties[c])

    def getBodyText(self):
        return self.context.getBodyText()

    @property
    def portal_catalog(self):
        return getToolByName(self.context, 'portal_catalog')

    @property
    def portal(self):
        return getToolByName(self.context, 'portal_url').getPortalObject()


class ExtensionProgramCountyView(FolderView):
    """
    Program County browser view
    """
    implements(IFolderView)
    
    def __init__(self, context, request):
        self.context = context
        self.request = request
        
        programs = {}
        counties = {}
        
        portal_catalog = self.portal_catalog

        all_programs = self.request.form.get('program')
        
        if not all_programs:
            all_programs = portal_catalog.uniqueValuesFor('Programs')
        elif isinstance(all_programs, str):
            all_programs = [all_programs]

        all_counties = self.request.form.get('county')
        
        if not all_counties:
            all_counties = portal_catalog.uniqueValuesFor('Counties')
        elif isinstance(all_counties, str):
            all_counties = [all_counties]
        
        for p in all_programs:
            programs[p] = {}
            for c in all_counties:
                programs[p][c] = []

        for c in all_counties:
            counties[c] = {}
            for p in all_programs:
                counties[c][p] = []
        
        for r in portal_catalog.searchResults({'portal_type' : 'FSDPerson'}):
            for p in r.extension_programs:
                for c in r.extension_counties:
                    if p in all_programs and c in all_counties:
                        programs[p][c].append(r)
                        counties[c][p].append(r)                  

        self.by_program = programs
        self.by_county = counties
        
    def getBodyText(self):
        return self.context.getBodyText()

    @property
    def portal_catalog(self):
        return getToolByName(self.context, 'portal_catalog')

    @property
    def portal(self):
        return getToolByName(self.context, 'portal_url').getPortalObject()



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
        self.request.response.setHeader('Content-Type', 'application/pdf')
        self.request.response.setHeader('Content-Disposition', 'attachment; filename="%s.pdf"' % self.context.getId())
        return self.createPDF()
    
    def createPDF(self):
    
        # -------------------------------------------------------------------------
        # Define functions used internally
        # -------------------------------------------------------------------------
    
        
        # Returns a reportlab image object based on a Plone image object
        
        def getImage(img_obj):
            img_width = img_obj.width
            img_height = img_obj.height
            if img_width > max_image_width:
                img_height = (max_image_width/img_width)*img_height
                img_width = max_image_width
            img_data = BytesIO(img_obj.data)
            return Image(img_data, width=img_width, height=img_height)
    
        
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
        
        
        # Provides the PDF entities for the corresponding HTML tags.
            
        def getContent(item):
            pdf = []
            if isinstance(item, Tag):
                className=item.get('class', '')
                item_type = item.name
                if item_type in ['h2', 'h3', 'h4', 'h5', 'h6']:
                    item_style = tag_to_style.get(item_type)
                    h = Paragraph(getItemText(item), styles[item_style])
                    h.keepWithNext = True
                    pdf.append(h)
                elif item_type in ['div']:
                    for i in item.contents:
                        pdf.extend(getContent(i))
                elif item_type in ['ul']:
                    for i in item.findAll('li'):
                        pdf.append(Paragraph('<bullet>&bull;</bullet>%s' % getInlineContents(i), bullet_list))
                elif item_type in ['p']:
                    # Pull images out of items and add before
                    for img in item.findAll('img'):
                        img.extract()
                        src = urljoin("/".join(self.context.getPhysicalPath()).replace('/'.join(self.site.getPhysicalPath()), ''), img['src'])
                        img_obj = self.site.restrictedTraverse(str(src.replace('/', '', 1)))
                        pdf_image = getImage(img_obj)
                        pdf.append(pdf_image)
                    if 'discreet' in className:
                        pdf.append(Paragraph(getInlineContents(item), discreet))
                    else:
                        pdf.append(Paragraph(getInlineContents(item), styles["Normal"]))
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
        
        # Clean up text
        text = text.replace('&nbsp;', ' ')
        
        # Colors
        header_rgb = (0.42,0.56,0.07)

        # Styles
        
        styles=getSampleStyleSheet()
        
        styles['Normal'].spaceBefore = 3
        styles['Normal'].spaceAfter = 6
        styles['Normal'].fontName = 'Times-Roman'
                
        styles['Heading1'].fontSize = 24
        
        styles['Heading2'].allowWidows = 0
        styles['Heading2'].fontSize = 13
        styles['Heading2'].textColor = header_rgb
        
        styles['Heading3'].allowWidows = 0
        styles['Heading3'].fontSize = 11
        styles['Heading3'].fontName = 'Helvetica'

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
        
        statement = ParagraphStyle('Statement')
        statement.fontSize = 9
        statement.fontName = 'Times-Roman'
        statement.spaceAfter = 6
        
        description = ParagraphStyle('Description')
        description.fontSize = 16
        description.spaceAfter = 8
        
        # Create document
        pdf_file = BytesIO()
        margin = 45
        doc = BaseDocTemplate(pdf_file,pagesize=letter,
                                rightMargin=margin,leftMargin=margin, showBoundary=0,
                                topMargin=margin,bottomMargin=margin)
        
        # Standard padding for document elements
        element_padding = 6
        
        #-------------- calculated coordinates/w/h
        
        # Extension image header
        header_image_width = 185.0
        header_image_x = doc.leftMargin + (doc.width-(header_image_width))/2
        header_image_padding = 3*element_padding
        
        header_image = self.site.portal_skins.agcommon_images['penn-state-extension-word-mark-white.png']
        header_image_data = BytesIO(header_image._data)
        header_image_height = (header_image_width/header_image.width)*header_image.height

        # Colored background box
        header_bg_y = doc.height + header_image_height
        header_bg_height = header_image_height + header_image_padding
        
        header_image_y = header_bg_y + (header_image_padding/2)
        
        # Factsheet title
        title_height = 90 # 1.25"
        
        # Document image setttings
        max_image_width = doc.width/2-18
        
        # Penn State/Extension Footer Image
        footer_image = self.site.portal_skins.agcommon_images['extension-factsheet-footer.png']
        footer_image_data = BytesIO(footer_image._data)
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
            canvas.drawImage(ImageReader(header_image_data), header_image_x, header_image_y, width=header_image_width, height=header_image_height, preserveAspectRatio=True,mask='auto')
            # Footer
            canvas.drawImage(ImageReader(footer_image_data), doc.leftMargin, doc.bottomMargin, width=doc.width, height=footer_image_height, preserveAspectRatio=True, mask='auto')
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
        title_frame1 = Frame(doc.leftMargin, title_column_y, doc.width/2-element_padding, title_column_height, id='title_col1')
        title_frame2 = Frame(doc.leftMargin+doc.width/2+element_padding, title_column_y, doc.width/2-element_padding,
                       title_column_height, id='title_col2')
        
        #Two Columns For remaining page
        
        other_frame1 = Frame(doc.leftMargin, doc.bottomMargin, doc.width/2-element_padding, doc.height, id='other_col1')
        other_frame2 = Frame(doc.leftMargin+doc.width/2+element_padding, doc.bottomMargin, doc.width/2-element_padding,
                       doc.height, id='other_col2')
        
        
        title_template = PageTemplate(id="title_template", frames=[title_frame_title,title_frame1,title_frame2],onPage=header_footer)
        other_template = PageTemplate(id="other_template", frames=[other_frame1,other_frame2],onPage=footer)
        
        doc.addPageTemplates([title_template,other_template])
        doc.handle_nextPageTemplate("other_template")
        
        # ---------------------------------------------------------------------        
        # Convert HTML to PDF (Magic goes here)
        # ---------------------------------------------------------------------

        # Soupify
        soup = BeautifulSoup(text)

        # This list holds the PDF elements
        pdf = []
        
        # Page heading and description in top frame, then framebreak into two
        # columns
        pdf.append(Paragraph(title, styles["Heading1"]))
        pdf.append(Paragraph(desc, description))
        pdf.append(FrameBreak())
    
        
        # Lead Image and caption as first elements. Not doing News Item image.
        leadImage_field = self.context.getField(IMAGE_FIELD_NAME)
        leadImage_caption_field = self.context.getField(IMAGE_CAPTION_FIELD_NAME)
        
        if leadImage_field and leadImage_caption_field:
            leadImage = leadImage_field.get(self.context)
            leadImage_caption = leadImage_caption_field.get(self.context)
            if leadImage.get_size():
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
        
        # All done with contents, appending line and statement
        pdf.append(HRFlowable(width='100%', spaceBefore=4, spaceAfter=4))
        
        statement_text = ("""Penn State College of Agricultural Sciences research and extension programs are funded in part by Pennsylvania counties, the Commonwealth of Pennsylvania, and the U.S. Department of Agriculture.                Where trade names appear, no discrimination is intended, and no endorsement by Penn State Cooperative Extension is implied.                 This publication is available in alternative media on request.                The Pennsylvania State University is committed to the policy that all persons shall have equal access to programs, facilities, admission, and employment without regard to personal characteristics not related to ability, performance, or qualifications as determined by University policy or by state or federal authorities. It is the policy of the University to maintain an academic and work environment free of discrimination, including harassment. The Pennsylvania State University prohibits discrimination and harassment against any person because of age, ancestry, color, disability or handicap, genetic information, national origin, race, religious creed, sex, sexual orientation, gender identity, or veteran status and retaliation due to the reporting of discrimination or harassment. Discrimination, harassment, or retaliation against faculty, staff, or students will not be tolerated at The Pennsylvania State University. Direct all inquiries regarding the nondiscrimination policy to the Affirmative Action Director, The Pennsylvania State University, 328 Boucke Building, University Park, PA 16802-5901; Tel 814-865-4700/V, 814-863-0471/TTY.                &copy The Pennsylvania State University %d
        """ % DateTime().year()).split("\n")
        
        for s in statement_text:
            if s.strip():
                pdf.append(Paragraph(s, statement))
        
        # Create PDF
        doc.build(pdf)

        # Pull PDF binary bits into variable, close file handle and return
        pdf_value = pdf_file.getvalue()
        pdf_file.close()
        return pdf_value