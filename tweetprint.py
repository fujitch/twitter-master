#!/usr/bin/env python
# coding: utf-8
  
import twitter
import twitkey
  
CONSUMER_KEY = twitkey.twkey['cons_key']
CONSUMER_SECRET = twitkey.twkey['cons_sec']
ACCESS_TOKEN_KEY = twitkey.twkey['accto_key']
ACCESS_TOKEN_SECRET = twitkey.twkey['accto_sec']
  
api = twitter.Api(consumer_key=CONSUMER_KEY,
                  consumer_secret=CONSUMER_SECRET,
                  access_token_key=ACCESS_TOKEN_KEY,
                  access_token_secret=ACCESS_TOKEN_SECRET)
tweets = api.GetSearch(term=u"#今日")
for tweet in tweets:
    print(tweet.text)