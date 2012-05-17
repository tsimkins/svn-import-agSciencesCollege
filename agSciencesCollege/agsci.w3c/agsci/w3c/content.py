from Products.CMFCore.utils import getToolByName
from BeautifulSoup import BeautifulSoup, Tag, NavigableString
from agsci.w3c import Report
import re




def setText(object, text):
    if object.portal_type in ['Folder']:
        object.folder_text.update(text, object)
    else:
        object.setText(text)
    object.reindexObject()


def getText(object):
    if object.portal_type in ['Folder']:
        text = object.folder_text()
    else:
        text = object.getText()
    return text


def getItemsWithText(context):
    portal_catalog = getToolByName(context, "portal_catalog")
    
    return portal_catalog.searchResults({'portal_type' : ['News Item', 'Event', 'Document', 'Folder', 'Topic']})


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
                                
        if found_auto and not dry_run:
            new_soup = soup.prettify()
            setText(o, new_soup)

    return report
    
    

def fixH2H3(context, dry_run=True):

    h3 = re.compile(r"<(/*)h3(.*?)>")
    
    report = Report(categories=['rightHeadings', 'wrongHeadings', 'noHeadings'])
    
    for r in getItemsWithText(context):
        o = r.getObject()
        text = getText(o)
        soup = BeautifulSoup(text)
        if soup('h2'):
            report.add('rightHeadings', o)
        elif soup('h3'):
            report.add('wrongHeadings', o)
        else:
            report.add('noHeadings', o)
    
    if not dry_run:
        for o in report.get('wrongHeadings'):
            text = getText(o)
            soup = BeautifulSoup(text).prettify()
            new_soup = h3.sub(r"<\g<1>h2\g<2>>", soup)
            setText(o, new_soup)

    return report
    
def fixLinkText(context, dry_run=True):

    report = Report(categories=['noLinks', 'okLinks', 'brokenLinks'])

    for r in getItemsWithText(context):
        o = r.getObject()
        text = getText(o)
        soup = BeautifulSoup(text)
        found_link = False
        found_empty_link = False
        found_no_links = False
                
        if soup('a'):
            for a in soup.findAll('a'):
                for i in a.contents:
                    if isinstance(i, NavigableString):
                        link_text = i
                    else:
                        link_text = link_text
                        
                    if link_text and 'http://' in link_text or 'https://' in link_text:
                        found_link = True
                    elif not link_text:
                        found_link = True
                        found_empty_link = True
        else:
            found_no_links = True
            
        if found_no_links:
            report.add('noLinks', o)
        elif found_link:
            report.add('brokenLinks', o)
        else:
            report.add('okLinks', o)                

        # Note: emptyLinks are also included in broken links.
        if found_empty_link:
            report.add('emptyLinks', o)


    return report
