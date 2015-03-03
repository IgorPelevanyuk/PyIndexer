import pymongo

connection_string = "mongodb://localhost"
connection = pymongo.MongoClient(connection_string)
monPyindexDB = connection.pyindex

VOC_PATH = 'ENRUS.TXT'

result = []
count = 0
current_word = ''
file_obj = file(VOC_PATH, 'r')
for line in file_obj:
    if (count%2 == 0):
        current_word = line.replace('\r\n', '').replace('\t', ' ').strip()
    else:
        result.append({current_word: line.replace('\r\n', '').replace('\t', ' ').strip()})
    count +=1
file_obj.close()

#print result
monPyindexDB.vocabulary.insert(result)
print 'DONE'