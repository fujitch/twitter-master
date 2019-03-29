# -*- coding: utf-8 -*-

'''
uttr呼びかけに対する
res応答を学習するLSTMモデルを出力
'''
import codecs
import sys
import numpy as np
import chainer
from chainer import cuda, Function, gradient_check, Variable, optimizers, serializers, utils
from chainer import Link, Chain, ChainList
import chainer.functions as F
import chainer.links as L

class seq2seq(chainer.Chain):
    def __init__(self, vocabNum, k, cocab):
        super(seq2seq, self).__init__(
            embed = L.EmbedID(vocabNum, k),
            H1 = L.LSTM(k, k),
            H2 = L.LSTM(k, k),
            H3 = L.LSTM(k, k),
            H4 = L.LSTM(k, k),
            H5 = L.LSTM(k, k),
            W = L.Linear(k, vocabNum),
            )

    def __call__(self, jline, eline, vocab):
        for i in range(len(jline)):
            wid = jvocab[jline[i]]
            x_k = self.embedx(Variable(np.array([wid], dtype=np.int32)))
            h = self.H(x_k)
        x_k = self.embedx(Variable(np.array([jvocab['<eos>']], dtype=np.int32)))
        tx = Variable(np.array([evocab[eline[0]]], dtype=np.int32))
        h = self.H(x_k)
        accum_loss = F.softmax_cross_entropy(self.W(h), tx)
        for i in range(len(eline)):
            wid = evocab[eline[i]]
            x_k = self.embedy(Variable(np.array([wid], dtype=np.int32)))
            next_wid = evocab['<eos>'] if (i == len(eline) - 1) else evocab[eline[i+1]]
            tx = Variable(np.array([next_wid], dtype=np.int32))
            h = self.H(x_k)
            loss = F.softmax_cross_entropy(self.W(h), tx)
            accum_loss += loss

        return accum_loss

# データの読み込み
fr  = codecs.open('inputs.txt', 'r', 'utf-8')
frs  = codecs.open('outputs.txt', 'r', 'utf-8')
replyText = fr.read()
replySourceText = frs.read()
fr.close()
frs.close()
replyText = replyText.split('\n')
replySourceText = replySourceText.split('\n')

replyTextList = replyText
replySourceTextList = replySourceText
    
# vocabulary作成
vocab = {}
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


demb = 100
epochs = 100
model = seq2seq(len(vocab), demb, vocab)
optimizer = optimizers.Adam()
optimizer.setup(model)

for epoch in range(epochs):
    for i in range(len(replySourceTextList)):
        model.H.reset_state()
        model.zerograds()
        loss = model(jlnr, eln, jvocab, evocab)
        loss.backward()
        loss.unchain_backward()
        optimizer.update()
        print i, " finished"        

    outfile = out_path + "/seq2seq-" + str(epoch) + ".model"
    serializers.save_npz(outfile, model)