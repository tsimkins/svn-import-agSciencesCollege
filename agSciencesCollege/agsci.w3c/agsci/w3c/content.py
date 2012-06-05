from Products.CMFCore.utils import getToolByName
from BeautifulSoup import BeautifulSoup, Tag, NavigableString
from agsci.w3c import Report
import re




def setText(object, text):
    if object.portal_type in ['Folder', 'PhotoFolder'] or object.meta_type in ['Blog', 'Subsite', 'Section', 'ATFolder', 'PhotoFolder', 'FormFolder']:
        object.folder_text.update(text, object)
    elif object.portal_type in ['FSDPerson']:
        object.setBiography(text)
    elif object.portal_type in ['File', 'Image', 'Link', 'FSDFacultyStaffDirectoryTool'] or object.portal_type.startswith('Form'):
        pass
    else:
        object.setText(text)
    object.reindexObject()


def getText(object):
    if object.portal_type in ['Folder', 'PhotoFolder'] or object.meta_type in ['Blog', 'Subsite', 'Section', 'ATFolder', 'PhotoFolder', 'FormFolder']:
        text = object.folder_text()
    elif object.portal_type in ['File', 'Image', 'Link', 'FSDFacultyStaffDirectoryTool'] or object.portal_type.startswith('Form'):
        text = ''
    elif object.portal_type in ['FSDPerson']:
        text = object.getBiography()
    else:
        text = object.getText()
    return text


def getItemsWithText(context):
    portal_catalog = getToolByName(context, "portal_catalog")

    return portal_catalog.searchResults({'portal_type' : ['News Item', 'Event', 'Document', 'Folder', 'Topic', 'HomePage', 'PhotoFolder', 'FSDPerson']})

def fixHeadingTags(context, dry_run=True):
    report = Report(categories=['headingsOK', 'headingsBold', 'headingsItalic', 'headingsBr'])

    def getNewTag(tag, heading):
        tag_regex = re.compile("</*%s>" % tag, re.I|re.M)
        return BeautifulSoup(tag_regex.sub('', str(heading))).contents[0]

    for r in getItemsWithText(context):
        o = r.getObject()
        text = getText(o)
        soup = BeautifulSoup(text)
        old_soup = soup.prettify()
        found_italic = False
        found_bold = False
        found_br = False
        
        for htag in ['h2', 'h3']:
            for h in soup.findAll(htag):
                for t in ['strong', 'b']:
                    if h(t):
                        found_bold = True
                        h.replaceWith(getNewTag(t, h))

                for t in ['br']:
                    for tag in h(t):
                        found_br = True
                        tag.extract()

                for t in ['em', 'i']:
                    if h(t):
                        # This is a special case, since we may legitimately have
                        # italicized words (latin names, etc.) inside headers.
                        # Only if it's going to be a dry run do we modify the 
                        # HTML so we can report on it.
                        if dry_run:
                            found_italic = True
                            h.replaceWith(getNewTag(t, h))
                        

        if found_bold:
            report.add('headingsBold', o)

        if found_italic:
            report.add('headingsItalic', o)
            
        if found_br:
            report.add('headingsBr', o)
            
        if found_bold or found_br or found_italic:
            new_soup = soup.prettify()
            report.addDiff(o, old_soup, new_soup)

            if not dry_run:
                setText(o, new_soup)

    return report

def fixPotentialHeadings(context, dry_run=True):
    report = Report(categories=['hasAutoFixableHeadings', 'hasManualFixableHeadings', 'noHeadings'])

    for r in getItemsWithText(context):
        o = r.getObject()
        text = getText(o)
        soup = BeautifulSoup(text)
        old_soup = soup.prettify()
        found_auto=False
        found_manual=False
        replaced_text = []

        for p in soup.findAll('p'):
            for c in ['\n', '\r', '\r\n']:
                while c in p.contents:
                    p.contents.remove(c)
            if len(p.contents) == 1:
                if isinstance(p.contents[0], Tag):
                    if p.contents[0].name in ['strong', 'b'] and len(p.contents[0]) == 1:
                        if not (soup('h2') or soup('h3')):
                            found_auto=True
                            p.replaceWith(BeautifulSoup('<h2>%s</h2>' % p.contents[0].text))
                            replaced_text.append(p.contents[0].text)
                        else:
                            found_manual=True

        if found_auto:
            report.add('hasAutoFixableHeadings', o)
        elif found_manual:
            report.add('hasManualFixableHeadings', o)
        else:
            report.add('noHeadings', o)

        if found_auto:
            new_soup = soup.prettify()
            report.addDiff(o, old_soup, new_soup)
        
            if not dry_run:
                setText(o, new_soup)

    return report



def fixH2H3(context, dry_run=True):

    h3 = re.compile(r"<(/*)h3(.*?)>")

    report = Report(categories=['rightHeadings', 'wrongHeadings', 'noHeadings'])

    for r in getItemsWithText(context):
        o = r.getObject()
        text = getText(o)

        try:
            soup = BeautifulSoup(text)
            old_soup = soup.prettify()
        except TypeError:
            import pdb; pdb.set_trace()
        if soup('h2'):
            report.add('rightHeadings', o)
        elif soup('h3'):
            report.add('wrongHeadings', o)
        else:
            report.add('noHeadings', o)

        for o in report.get('wrongHeadings'):
            text = getText(o)
            soup = BeautifulSoup(text).prettify()
            new_soup = h3.sub(r"<\g<1>h2\g<2>>", soup)
            report.addDiff(o, old_soup, new_soup)
            if not dry_run:
                setText(o, new_soup)

    return report

def fixLinkText(context, dry_run=True):

    report = Report(categories=['noLinks', 'okLinks', 'brokenLinks'])

    for r in getItemsWithText(context):
        o = r.getObject()
        text = getText(o)
        soup = BeautifulSoup(text)
        old_soup = soup.prettify()
        found_link = False
        found_empty_link = False
        found_no_links = False

        if soup('a'):
            for a in soup.findAll('a'):
                link_text = ""
                url_link = False
                empty_link = False
                for i in a.contents:
                    if isinstance(i, NavigableString):
                        link_text = i
                    else:
                        link_text = str(i)

                    if link_text and 'http://' in link_text or 'https://' in link_text:
                        found_link = True
                        url_link = True
                    elif not link_text:
                        found_link = True
                        found_empty_link = True
                        empty_link = True

                if url_link:
                    a.contents.append(NavigableString(' -- REPLACE WITH CORRECT LINK TEXT'))
                if empty_link:
                    a.contents.append(NavigableString('-- EMPTY LINK --'))
        else:
            found_no_links = True

        if found_no_links:
            report.add('noLinks', o)
        elif found_link:
            report.add('brokenLinks', o)
            new_soup = soup.prettify()
            report.addDiff(o, old_soup, new_soup)
        else:
            report.add('okLinks', o)

        # Note: emptyLinks are also included in broken links.
        if found_empty_link:
            report.add('emptyLinks', o)


    return report
