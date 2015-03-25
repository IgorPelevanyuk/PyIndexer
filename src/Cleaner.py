import pymongo
import inspector
#
# This module is able to clean frequency database by checking if the word could
# be found in other collections (EWORDS.TXT or db.vocabulary) 
#
connection_string = "mongodb://admin:pass@vm162.jinr.ru:27017"
connection = pymongo.MongoClient(connection_string)
monPyindexDB = connection.pyindex

f = open('EWORDS.TXT', 'r+')
word_base = {}
for word in f:
    word_base[word[:-2]] = 1
    
voc_base = []
cursor = monPyindexDB.vocabulary.find()
for word in cursor:
    voc_base.append(word['word'])
cursor.close()

cursor = monPyindexDB.index.find()
total_sum = 0
total_count = 0
count = 0
print cursor.count()
for word in cursor:
    candidates = inspector.checkWord(word['word'])
    if (len(candidates) != 0):
        print word['word'], ': ', candidates 
    total_sum += word['count']
    total_count += 1
    if (word['word'] not in word_base) and (word['word'] not in voc_base):
        count += 1
        #print word['word']
cursor.close()
    # break

print 'Total amount of used words: ', total_sum
print 'Total amount of unique words: ', total_count

print '\r\n Number of unresolved unique words', count