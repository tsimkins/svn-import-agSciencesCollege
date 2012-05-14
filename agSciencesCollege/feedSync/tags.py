import urllib2
import re
    
data = {
    'extension': ['Cooperative_Extension', 'Penn_State_Cooperative_Extension', 'Extension', 'Penn_State_Extension'],
    'aec' : ['Earth_and_Environment', 'Chesapeake_Bay', 'energy', 'water', 'water_quality', 'environmental_engineering',
             'environment', 'environmental_stewardship', 'forestry']
}


def setTags(context, tag):
    # Tag Feeds
    
    print "Settings %s within %s" % (tag, context.absolute_url())

    if tag not in data.keys():
        return False
    else:
        urls = data[tag] 

    print "Urls to search: %s" % ",".join(urls)
    
    linkRegex = re.compile("<link>http://live.psu.edu/story/(\d+).*?</link>", re.I|re.M)
    
    found_articles = False
    
    for u in urls:
        rss = urllib2.urlopen('http://live.psu.edu/tagrss/%s' % u).read()
        for m in re.finditer(linkRegex, rss):
            link = m.group(1)
            if link in context.objectIds():
                story = context[link]
                subject = list(story.Subject())
                if not subject.count('news-%s' % tag):
                    subject.append('news-%s' % tag)
                    print "New subject for %s : %s" % (link, str(subject))
                    found_articles = True
                    story.setSubject(tuple(subject))
                    story.reindexObject()
                    
    return found_articles
    
    