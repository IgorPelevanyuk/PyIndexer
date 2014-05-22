import pymongo

connection_string = "mongodb://localhost"
connection = pymongo.MongoClient(connection_string)
monPyindexDB = connection.pyindex

f = open('EWORDS.TXT', 'r+')
words = {}
for word in f:
    words[word[:-2]] = 1

cursor = monPyindexDB.index.find()
summa = 0
count = 0
total_sum = 0
total_count =0
for word in cursor:
    # print len(word['word'])
    # print word['word']
    total_sum += word['count']
    total_count += 1
    if word['word'] not in words:
        summa += word['count']
        count += 1
        if word['count']>1000:
            print word['word']
    # break

print summa
print count

print total_sum
print total_count