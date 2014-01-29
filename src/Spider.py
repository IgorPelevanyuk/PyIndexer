import string
import re
import pickle
from operator import itemgetter
import pymongo

connection_string = "mongodb://localhost"
connection = pymongo.MongoClient(connection_string)
monPyindexDB = connection.pyindex

def getOneUncrawled():
    uncrawled = monPyindexDB.tocrawl.find_one()
    return uncrawled['url']

def setCrawled(url):
    monPyindexDB.tocrawl.remove({'url':url})
    monPyindexDB.crawled.insert({'url':url})

def setUncrawled(url_list):
    for url in url_list:
        if not isAcceptable(url):
            continue
        craw_cursor = monPyindexDB.crawled.find({'url':url})
        uncraw_cursor = monPyindexDB.tocrawl.find({'url':url})
        if craw_cursor.count()==0 and uncraw_cursor.count()==0:
            monPyindexDB.tocrawl.insert({'url':url})

def addWords(word_dict):
    for word in word_dict:
        monPyindexDB.index.update({'word':word}, {'$inc':{'count':word_dict[word]}}, upsert=True)
    

#-------------------------------------------------------------------------------

def isAcceptable(url):
    if url == "http://www.bbc.co.uk":
        return True
    if '?' in url:
        return False
    if url[-4:]=='.stm':
        return False
    if url.find("http://www.bbc.co.uk/news/")==0:
        return True
    else:
        return False

def get_page(url):
    try:
        import urllib
        if(isAcceptable(url)):
            page = urllib.urlopen(url).read()
        if 'xml:lang="en-GB"' in page:
            return page
        else:
            return ""
    except:
        return ""

def addToIndex(page):
    page = string.lower(page)
    current = re.search(ur"[a-z,',`]+", page)
    voc = {}
    while current:
        if current.group() in voc:
            voc[current.group()]+=1
        else:
            voc[current.group()]=1
        page = page[page.index(current.group())+len(current.group()):]
        current = re.search(ur"[a-z'`]+", page)
    addWords(voc)
    print len(voc)

def addAllLinks(page):
    links = []
    current = re.search(ur"href=\"[^\"]+\"", page)
    while (current):
        links+=[current.group()[6:-1]] if "http:" in current.group()[6:-1] else ["http://www.bbc.co.uk"+current.group()[6:-1]]
        page = page[page.index(current.group())+len(current.group()):]
        current = re.search(ur"href=\"[^\"]+\"", page)
    return links

def dryPage(page):
    current = re.search(ur"[\r\n]+", page)
    while (current):
        page = page.replace (current.group(), ' ')
        current = re.search(ur"[\r\n]+", page)

    current = re.search(ur"<script[^>]*>[\S\s]*?<\/script[^>]*>", page)
    while (current):
        page = page.replace (current.group(), ' ')
        current = re.search(ur"<script[^>]*>[\S\s]*?<\/script[^>]*>", page)

    current = re.search(ur"<style[^>]*>[\S\s]*?<\/style[^>]*>", page)
    while (current):
        page = page.replace (current.group(), ' ')
        current = re.search(ur"<style[^>]*>[\S\s]*?<\/style[^>]*>", page)

    current = re.search(ur"<[^>]+>", page)
    while (current):
        page = page.replace (current.group(), ' ')
        current = re.search(ur"<[^>]+>", page)

    current = re.search(ur"&[#0-9a-z]*;", page)
    while (current):
        page = page.replace (current.group(), "'")
        current = re.search(ur"&[#0-9a-z]*;", page)

    current = re.search(ur"( ')|(' )", page)
    while (current):
        page = page.replace (current.group(), ' ')
        current = re.search(ur"( ')|(' )", page)

    current = re.search(ur"[A-Z]", page)
    while (current):
        page = page.replace (current.group(), '')
        current = re.search(ur"[A-Z]", page)

    current = re.search(ur"'[a-z]*", page)
    while (current):
        page = page.replace (current.group(), '')
        current = re.search(ur"'[a-z]*", page)



    page = ' '.join(page.split())
    stamp_text = "Services Mobile Connected"
    if stamp_text in page:
        index = page.find(stamp_text)
        page = page[:index]

    return page

#-------------------------------------------------------------------------------
class Spider:

    def __init__(self):
        pass

    def clearDB(self):
        monPyindexDB.tocrawl.remove()
        monPyindexDB.index.remove()
        monPyindexDB.crawled.remove()
        monPyindexDB.tocrawl.insert({'url':"http://www.bbc.co.uk"})

    def crawl(self, amount):
        i=0
        while (i<amount):                    # AND toCrawl exists!!!
            url = getOneUncrawled()
            page = get_page(url)
            setUncrawled( addAllLinks(page) )
            page = dryPage(page)
            addToIndex(page)
            setCrawled(url)
            print str(i)+" - "+url +"     //"
            if page!='':
                i+=1