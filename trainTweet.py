# -*- coding: utf-8 -*-

import codecs
import janome.tokenizer

# データの読み込み
fn  = codecs.open('./text/normal.txt', 'r', 'utf-8')
fr  = codecs.open('./text/reply.txt', 'r', 'utf-8')
frs  = codecs.open('./text/replySource.txt', 'r', 'utf-8')
normalText = fn.read()
replyText = fr.read()
replySourceText = frs.read()
fn.close()
fr.close()
frs.close()
normalText = normalText.split('\n')
replyText = replyText.split('\n')
replySourceText = replySourceText.split('\n')

normalTextList = []
replyTextList = []
replySourceTextList = []
t = janome.tokenizer.Tokenizer()
for line in normalText:
    tokens = t.tokenize(line)
    normalTextList.append([token.surface for token in tokens])
for line in replyText:
    tokens = t.tokenize(line)
    replyTextList.append([token.surface for token in tokens])
for line in replySourceText:
    tokens = t.tokenize(line)
    replySourceTextList.append([token.surface for token in tokens])
    
# vocabulary作成
vocab = {}
for i in range(len(normalTextList)):
    words = normalTextList[i]
    for word in words:
        if word not in vocab:
            vocab[word] = len(vocab)
for i in range(len(replyTextList)):
    words = replyTextList[i]
    for word in words:
        if word not in vocab:
            vocab[word] = len(vocab)
for i in range(len(replySourceTextList)):
    words = replySourceTextList[i]
    for word in words:
        if word not in vocab:
            vocab[word] = len(vocab)
vocab['<eos>'] = len(vocab)

