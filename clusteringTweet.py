# -*- coding: utf-8 -*-

import codecs
import pickle
import twitkey
from requests_oauthlib import OAuth1Session
import json
import datetime, time, sys

CK = twitkey.twkey['cons_key']
CS = twitkey.twkey['cons_sec']
AT = twitkey.twkey['accto_key']
AS = twitkey.twkey['accto_sec']

session = OAuth1Session(CK, CS, AT, AS)
#pickle読み込み
with open('random2.pickle', mode='rb') as f:
    list = pickle.load(f)
    
normalTweets = ''
replyTweets = ''
replySourceTweets = ''
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

def processing_tweet(tweet, text):
    #URLを除く
    if len(tweet['entities']['urls']) > 0:
        for url in tweet['entities']['urls']:
            urlText = url['url']
            text = text.replace(urlText, '')
    #ハッシュタグも難しいので除く
    if len(tweet['entities']['hashtags']) > 0:
        for hashtag in tweet['entities']['hashtags']:
            hashtagText = '#' + hashtag['text']
            text = text.replace(hashtagText, '')
    #改行を省く
    text = text.replace('\n', '')
    #空白を除く
    text = text.replace(' ', '')
    text = text.replace('　', '')
    return text

def processing_reply(tweet, text):
    text = processing_tweet(tweet, text)
    if tweet['in_reply_to_screen_name'] != None:
        toName = '@' + tweet['in_reply_to_screen_name']
        text = text.replace(toName, '')
    return text

def checkText(text):
    if text.find('http') != -1:
        return True
    if text.find('@') != -1:
        return True
    if text.find('#') != -1:
        return True
    return False

def getOneTweet(status_id, session):
    url = 'https://api.twitter.com/1.1/statuses/show.json'
    params = {'id':status_id}
    try:
        res = session.get(url, params = params)
        if res.status_code != 200:
            return None
        return json.loads(res.text)
    except:
        return None

limit = checkLimit(session)
limit = limit['resources']
limit = limit['statuses']
limit = limit['/statuses/show/:id']
remaining = limit['remaining']
reset = limit['reset']
print('API制限:')
print(remaining)
offsetCount = 0
for tweets in list:
    for tweet in tweets:
        text = tweet['text']
        #埋め込みリツイートは難しいので省く
        if 'RT' in text or 'RT' in text:
            continue
        #普通のツイートの時の処理
        if tweet['in_reply_to_status_id'] == None:
            text = processing_tweet(tweet, text)
            # prosessしてもダメそうな奴は諦める(二重リプライ、無効なurl、無効なハッシュタグ)
            if checkText(text):
                continue
            if normalTweets == '':
                normalTweets = text
            else:
                normalTweets = normalTweets + '\n' + text
            print(text)
        #リプライの時の処理(リプライと元のツイート取得)
        else:
            #リプライ元のツイート取得
            replyTweet = getOneTweet(tweet['in_reply_to_status_id'], session)
            offsetCount += 1
            if offsetCount > remaining - 5:
                waitUntilReset(reset)
                limit = checkLimit(session)
                limit = limit['resources']
                limit = limit['statuses']
                limit = limit['/statuses/show/:id']
                remaining = limit['remaining']
                reset = limit['reset']
                print('API制限:')
                print(remaining)
                offsetCount = 0
            if replyTweet == None:
                continue
            replyText = replyTweet['text']
            replyText = processing_reply(replyTweet, replyText)
            text = processing_reply(tweet, text)
            # prosessしてもダメそうな奴は諦める(二重リプライ、無効なurl、無効なハッシュタグ)
            if checkText(text):
                continue
            if checkText(replyText):
                continue
            if replyTweets == '':
                replyTweets = text
            else:
                replyTweets = replyTweets + '\n' + text
            if replySourceTweets == '':
                replySourceTweets = replyText
            else:
                replySourceTweets = replySourceTweets + '\n' + replyText
            print(text)
            print(replyText)
                
fn = codecs.open('normal.txt', 'w', 'utf-8')
fr = codecs.open('reply.txt', 'w', 'utf-8')
frs = codecs.open('replySource.txt', 'w', 'utf-8')

fn.write(normalTweets)
fr.write(replyTweets)
frs.write(replySourceTweets)

fn.close()
fr.close()
frs.close()