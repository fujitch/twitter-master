# -*- coding: utf-8 -*-

import twitter
import twitkey
from random import randint
import pickle
import unicodedata

CONSUMER_KEY = twitkey.twkey['cons_key']
CONSUMER_SECRET = twitkey.twkey['cons_sec']
ACCESS_TOKEN_KEY = twitkey.twkey['accto_key']
ACCESS_TOKEN_SECRET = twitkey.twkey['accto_sec']
  
api = twitter.Api(consumer_key=CONSUMER_KEY,
                  consumer_secret=CONSUMER_SECRET,
                  access_token_key=ACCESS_TOKEN_KEY,
                  access_token_secret=ACCESS_TOKEN_SECRET)

def is_japanese(string):
    for ch in string:
        try:
            name = unicodedata.name(ch) 
        except:
            return False
        if "HIRAGANA" in name \
        or "KATAKANA" in name:
            return True
    return False


list = []
count = 0
while count < 100:
    i = randint(1,500000000)
    print(count)
    try:
        user = api.GetUser(i)
    except:
        continue
    if is_japanese(user.description) == False:
        if not user.time_zone in [u'Osaka', u'Tokyo', u'Sapporo']:
            continue
    if user.protected == True:
        continue
    tweets = api.GetUserTimeline(user_id=i, count=200)
    if len(tweets) != 200:
        continue
    list.append(tweets)
    count += 1
    
with open('random1.pickle', mode='wb') as f:
    pickle.dump(list, f, protocol=2)
    
    
