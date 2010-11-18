#!/usr/bin/python

import feedparser
from agsci.apdfeeds import texttime
from datetime import datetime
from pytz import utc, timezone
from urllib import quote_plus

def getItems(search_term="", banned_ids=[], search_url="", my_tz="US/Eastern"):

    results = []
    
    tz = timezone(my_tz)
    
    if search_url:
        feed_url = search_url        
    else:
        feed_url = "http://search.twitter.com/search.atom?q=%s" % quote_plus(search_term)

        
    feed = feedparser.parse(feed_url)
    
    current_time = datetime.now(tz)
    
    for item in feed['entries']:
        for key in item.keys():
           
            title = item.get("title")
            author = item.get("author")
            links = item.get("links")
            published_parsed = item.get("published_parsed", item.get('updated_parsed'))[0:7] + (utc,)
    
            author_image = None
    
            if links:
                for l in links:
                    if l.get("rel") == 'image':
                        author_image = l.get('href')
            item_time = datetime(*published_parsed).astimezone(tz)
            datestamp = datetime(*published_parsed).astimezone(tz).strftime('%m/%d/%Y %I:%M %p')
        
        if not banned_ids.count(author.split()[0].lower()):
            results.append({
                'title' : title,
                'author' : author,
                'item_time' : "%s ago" % texttime.stringify(current_time - item_time),
                'author_image' : author_image,
            })
        
    return results