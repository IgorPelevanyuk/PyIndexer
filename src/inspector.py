import pymongo
#
# This module is supposed to help to remove endings from words
#
RULES = [# Plural
         {'ending':'ses', 'correction':'s'},
         {'ending':'xes', 'correction':'x'},
         {'ending':'shes', 'correction':'sh'},
         {'ending':'ches', 'correction':'ch'},
         # ------
         {'ending':'ies', 'correction':'y'},
         {'ending':'oes', 'correction':'o'},
         {'ending':'ves', 'correction':'f'},
         {'ending':'s', 'correction':''},
         # ED
         {'ending':'??ed', 'correction':'?'},
         {'ending':'ied', 'correction':'y'},
         {'ending':'ed', 'correction':'e'},
         {'ending':'ed', 'correction':''},
         # ING
         {'ending':'ying', 'correction':'ie'},
         {'ending':'??ing', 'correction':'?'},
         {'ending':'ing', 'correction':'e'},
         {'ending':'ing', 'correction':''},
         ]

def checkWord(word):
    candidates = []
    for rule in RULES:
        if ('??'  in rule):
            continue
        if word.endswith(rule['ending']):
            end_len = len(rule['ending'])
            candidates.append(word[:( - end_len)] + rule['correction'])
    return candidates
            