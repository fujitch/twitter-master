# -*- coding: utf-8 -*-

from requests_oauthlib import OAuth1Session
import json
import datetime, time, sys
import twitkey
from random import randint
import unicodedata
import pickle

CONSUMER_KEY = twitkey.twkey['cons_key']
CONSUMER_SECRET = twitkey.twkey['cons_sec']
ACCESS_TOKEN_KEY = twitkey.twkey['accto_key']
ACCESS_TOKEN_SECRET = twitkey.twkey['accto_sec']
 
CK = twitkey.twkey['cons_key']
CS = twitkey.twkey['cons_sec']
AT = twitkey.twkey['accto_key']
AS = twitkey.twkey['accto_sec']

session = OAuth1Session(CK, CS, AT, AS)

def checkLimit(session):
        '''
        回数制限を取得
        '''
        url = "https://api.twitter.com/1.1/application/rate_limit_status.json"
        res = session.get(url)
        return json.loads(res.text)
 
def waitUntilReset(reset):
        '''
        reset 時刻まで sleep
        '''
        seconds = reset - time.mktime(datetime.datetime.now().timetuple())
        seconds = max(seconds, 0)
        print ('\n     =====================')
        print ('     == waiting %d sec ==' % seconds)
        print ('     =====================')
        sys.stdout.flush()
        time.sleep(seconds + 10)  # 念のため + 10 秒
    
def getUser(remaining, session):
    '''
    限界までApiを叩き、ユーザーリスト取得
    '''
    users = []
    count = 0
    while count < remaining:
        user_id = randint(1, 500000000)
        url = 'https://api.twitter.com/1.1/users/show.json'
        params = {'user_id':user_id}
        try:
            res = session.get(url, params = params)
            if res.status_code != 200:
                count += 1
                continue
            users.append(json.loads(res.text))
            count += 1
        except:
            count += 1
            continue
    return users

def getTweetsByUserId(user_id, session, count):
    '''
    ユーザーのツイートをuser_idから取得
    '''
    url = 'https://api.twitter.com/1.1/statuses/user_timeline.json'
    params = {'user_id':user_id, 'count':count}
    try:
        res = session.get(url, params = params)
        if res.status_code != 200:
            return None
        return json.loads(res.text)
    except:
        return None
    
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
    

userList = []
count = 0
# まず日本人ユーザーを取得
while count < 100:
    
    # api制限チェック
    limit = checkLimit(session)
    limit = limit['resources']
    limit = limit['users']
    limit = limit['/users/show/:id']
    remaining = limit['remaining']
    reset = limit['reset']
    print('ユーザー取得')
    print('API制限:')
    print(remaining)
    if remaining - 5 < 1:
        waitUntilReset(reset)
        continue
    # userリスト取得
    users = getUser(remaining - 5, session)
    if len(users) == 0:
        # 制限解除までスリープ
        waitUntilReset(reset)
        continue
    
    for user in users:
        if user == None:
            continue
        if is_japanese(user['description']) == False:
            if not user['time_zone'] in [u'Osaka', u'Tokyo', u'Sapporo']:
                print('Not Japanese')
                continue
        if user['protected'] == True:
            print('protected')
            continue
        userList.append(user)
        count += 1
    print(count)
    # 制限解除までスリープ
    waitUntilReset(reset)

    
getCount = 0
tweetsList = []
# ツイート取得
while True:
    # api制限チェック
    limit = checkLimit(session)
    limit = limit['resources']
    limit = limit['statuses']
    limit = limit['/statuses/user_timeline']
    remaining = limit['remaining']
    reset = limit['reset']
    print('ツイート取得')
    print('API制限:')
    print(remaining)
    if remaining - 5 < 1:
        waitUntilReset(reset)
        continue
    if len(userList) <= getCount + remaining - 5:
        for user in userList:
            tweets = getTweetsByUserId(user['id'], session, 200)
            if tweets != None:
                tweetsList.append(tweets)
        break
    if len(userList) > getCount + remaining - 5:
        for i in range(remaining-5):
            user = userList[getCount+i]
            tweets = getTweetsByUserId(user['id'], session, 200)
            if tweets != None:
                tweetsList.append(tweets)
    getCount += remaining - 5
    # 制限解除までスリープ
    waitUntilReset(reset)
    
with open('random2.pickle', mode='wb') as f:
    pickle.dump(tweetsList, f, protocol=2)