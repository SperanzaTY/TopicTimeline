import mxnet as mx
from mxnet import gluon, autograd, nd, init
from mxnet.gluon import nn, rnn
import gluonnlp as nlp
import numpy as np
import jieba
import time

class BiLSTM(nn.Block):
    def __init__(self, hidden_size, num_layers=1, **kwargs):
        super(BiLSTM, self).__init__(**kwargs)
        with self.name_scope():
            self.rnn = rnn.LSTM(hidden_size=hidden_size, num_layers=num_layers, bidirectional=True)

    def forward(self, x):
        output = self.rnn(x)
        return output

def load_data(dataset_path, stopwords_path):
    with open(dataset_path, 'r', encoding='utf-8') as file:
        data = file.readlines()

    with open(stopwords_path, 'r', encoding='utf-8') as file:
        stopwords = [line.strip() for line in file.readlines()]

    sentences, labels = [], []
    for line in data:
        parts = line.strip().split(',,')
        sentence = parts[0].strip()
        label = int(parts[1].strip())
        sentences.append(sentence)
        labels.append(label)
    return sentences, labels, stopwords

def preprocess(sentences, stopwords):
    sentences = [' '.join([word for word in jieba.cut(sentence) if word not in stopwords]) for sentence in sentences]

    counter = nlp.data.Counter()
    for sentence in sentences:
        counter.update(sentence.split())

    start_time = time.time()
    vocab = nlp.Vocab(counter, max_size=10000)
    end_time = time.time()
    print(f'Vocabulary building time: {end_time-start_time} seconds')

    def token_to_idx(x):
        return vocab[x.split()]

    sentences = list(map(token_to_idx, sentences))

    return sentences, vocab

def pad_sequences(sentences, sequence_length=100):
    for i in range(len(sentences)):
        sentences[i] = sentences[i][:sequence_length]
        sentences[i] += [0] * max(0, sequence_length - len(sentences[i]))
    return np.array(sentences)

def bi_lstm_model(vocab_size, num_embed, num_hidden, num_layers):
    net = nn.Sequential()
    with net.name_scope():
        net.add(nn.Embedding(input_dim=vocab_size, output_dim=num_embed),
                BiLSTM(num_hidden),
                nn.Dense(64, activation='relu'),
                nn.Dense(1, activation='sigmoid'))

    net.initialize(init=mx.init.Xavier())
    return net

sentences, labels, stopwords = load_data('goods_zh.txt', 'stopword.txt')
sentences, vocab = preprocess(sentences, stopwords)
padded_sentences = pad_sequences(sentences)

net = bi_lstm_model(len(vocab) + 1, 64, 64, 1)
loss = gluon.loss.SigmoidBCELoss()
trainer = gluon.Trainer(net.collect_params(), 'adam', {'learning_rate': 0.005})

epochs = 10
batch_size = 1
output_interval = 10000

for epoch in range(10):
    train_loss = 0.0
    train_acc = mx.metric.Accuracy()
    start_time = time.time()

    for i in range(len(sentences)):
        sentence = nd.array(padded_sentences[i]).reshape((1, -1))
        label = nd.array(labels[i]).reshape((1, 1))

        with autograd.record():
            output = net(sentence)
            L = loss(output, label)
        L.backward()
        trainer.step(1)

        train_loss += nd.mean(L).asscalar()
        train_acc.update(label, output)

        if (i+1) % output_interval == 0:
            print(f'Epoch {epoch + 1} | Processed {i+1} samples | Loss: {train_loss / (i + 1):.4f}, Acc: {train_acc.get()[1]:.4f}')
            train_loss = 0.0
            train_acc.reset()

    print(f'Epoch {epoch + 1} done. Loss: {train_loss / len(sentences):.4f}, Acc: {train_acc.get()[1]:.4f}')
    end_time = time.time()
    print(f'Epoch {epoch + 1} time: {end_time - start_time} seconds')

net.save_parameters('mind_model.mxnet')