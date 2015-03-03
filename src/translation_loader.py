import pymongo
#
# This module loads vocabulary from the file ENRUS.TXT. It expects that on the 
# odd lines there are English word and on the even is the translation. 
#
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
        result.append({'word':current_word, 'translation':line.replace('\r\n', '').replace('\t', ' ').strip()})
    count +=1
file_obj.close()

monPyindexDB.vocabulary.insert(result)
print 'DONE'