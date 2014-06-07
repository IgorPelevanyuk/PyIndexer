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

def getIndexesFromDB():
    indexes = {}
    cursor = monPyindexDB.index.find()
    for i in range(0, cursor.count()):
        indexes[cursor[i]['word']] = cursor[i]['count']
    return indexes

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
    page = page.lower()
    # print "______________________"
    # print page
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

    current = re.search(ur"[A-Z0-9]{2,}", page)
    while (current):
        page = page.replace (current.group(), '')
        current = re.search(ur"[A-Z0-9]{2,}", page)

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

class TxtSpider(Spider):
    
    def __init__(self):
        self.names = {}
        self.decapitalised = set('i')
        self.index = {}
        self.removed1 = 0
        self.removed2 = 0
        pass
    
    def _addToLocalIndex(self, text):
        text = text.lower()
        current = re.search(ur"[a-z]+", text)
        while current:
            if current.group() in self.index:
                self.index[current.group()]+=1
            else:
                self.index[current.group()]=1
            text = text[text.index(current.group())+len(current.group()):]
            current = re.search(ur"[a-z]+", text)
        
    
    def _findNames(self, line):
        copy_of_line = line
        #current = re.search(ur"\s*[a-z][^\.\n\!\?]\s+[A-Z][A-Za-z]+", copy_of_line)
        current = re.search(ur"[A-Z][a-z]+", copy_of_line)
        while (current):
            copy_of_line = copy_of_line.replace(current.group(), '', 1)
            current = re.search(ur"[A-Z][a-z]+", copy_of_line)
            self.removed2 += 1
        current = re.search(ur"[a-z]+", copy_of_line)
        while (current):
            self.decapitalised.add(current.group())
            copy_of_line = copy_of_line.replace(current.group(), '',1)
            current = re.search(ur"[a-z]+", copy_of_line)
    
    def dry(self, line):
        self._findNames(line)
        line = line.lower()
        current = re.search(ur"[^A-Za-z\s]+", line)
        while (current):
            line = line.replace (current.group(), ' ',1)
            current = re.search(ur"[^A-Za-z\s]+", line)
        return line
    
    def crawl(self, path):
        file_obj = file(path, 'r')
        for line in file_obj:            
            line = self.dry(line)
            self._addToLocalIndex(line)
        file_obj.close()
        for name in self.index.keys():
            if (name not in self.decapitalised):
                del self.index[name]
        print len(self.index)
        for name in sorted(self.index.items(), key = lambda x: x[1]):
            print name[0], ' ', self.index[name[0]]
        print sum(self.index.values())
        print self.removed1
        print self.removed2
        print self.removed1 + sum(self.index.values())
        addWords(self.index)
            

x = TxtSpider()
x.clearDB()
x.crawl('/home/igor/Desktop/dg.txt')
            