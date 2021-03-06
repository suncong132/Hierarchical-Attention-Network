import numpy as np
from collections import Counter
import random
import math

def load_data(data_path):
    """
    载入数据
    """
    data= []
    labels = []
    ids = []
    max_sentence_len = 0
  
    with open(data_path, 'r') as f:
        for line in f:
            line = line.strip()
            line_list = line.split('\t')
            one_data = line_list[1].split(' ')
            label = int(line_list[2])
            tmp_len = len(one_data)
            if tmp_len > max_sentence_len:
                max_sentence_len = tmp_len
           # if tmp_len <= 2000:
               # data.append([discretization(i) for i in one_data])
            ids.append(line_list[0])
            data.append(one_data)
            labels.append(label)
        f.close()
    print("max sentence length: ", max_sentence_len)
    return ids, data, labels

def build_vocabulary(data, min_count=3):
    """
    基于所有数据构建词表
    """
    # add <PAD> for embedding
    count = [('<UNK>', -1), ('<PAD>', -1)]
    # count = [('UNK', -1)]
    words = []
    for line in data:
        words.extend(line)  #TODO ?
    counter = Counter(words)
    counter_list = counter.most_common()
    for word, c in counter_list:
        if c >= min_count:
            count.append((word, c))
    dict_word2index = dict()
    for word, _ in count:
        dict_word2index[word] = len(dict_word2index)
    dict_index2word = dict(zip(dict_word2index.values(), dict_word2index.keys()))
    print("vocab size:", len(count))
    print(count[-1])
    return count, dict_word2index, dict_index2word

def split_data(data, radio=0.7):
    """
    将训练集分给为训练集和检验集
    """
    split_index = int(len(data) * radio)
    new_data1 = data[ : split_index]
    new_data2 = data[split_index : ]
    return new_data1, new_data2

def build_data_set_HAN(data, labels, dict_word2index, num_sentences, sequence_length):
    """
    基于词表构建数据集（数值化）
    """
    dataset = []
    indices = np.arange(len(labels))
#    np.random.shuffle(indices)
    new_labels = []
    for i in indices:
        new_labels.append(labels[i]-1)
        new_line = []
        for word in data[i]:
            if word in dict_word2index:
                index = dict_word2index[word]
            else:
                index = 0    # <UNK>
            new_line.append(index)
        line_splitted = sentences_splitted(text=new_line, split_chars=[dict_word2index[split_label] for split_label in ['。', '！', '？']])
        # 向后补齐sequence_length
        for ls_i, ls in enumerate(line_splitted):
            line_splitted[ls_i] = sentence_padding(sentence=ls, max_length=sequence_length)
        # 向后补齐num_sentences
        pad_num = num_sentences - len(line_splitted)
        if pad_num < 0:
            line_splitted = line_splitted[-1*num_sentences:]
        while pad_num > 0:
            line_splitted.append([1 for _ in range(sequence_length)])  # <PAD>
            pad_num -= 1
        dataset.append(line_splitted)
    print(np.shape(dataset))
    # [total_size, num_sentences, sequence_length]
    return np.array(dataset, dtype=np.int64), np.array(new_labels, dtype=np.int64)

def build_test_data_HAN(data, dict_word2index, num_sentences, sequence_length):
    """
    基于词表构建数据集（数值化）
    """
    dataset = []
    indices = np.arange(len(data))
#    np.random.shuffle(indices)
    new_labels = []
    for i in indices:
        new_line = []
        for word in data[i]:
            if word in dict_word2index:
                index = dict_word2index[word]
            else:
                index = 0    # <UNK>
            new_line.append(index)
        line_splitted = sentences_splitted(text=new_line, split_chars=[dict_word2index[split_label] for split_label in ['。', '！', '？']])
        # 向后补齐sequence_length
        for ls_i, ls in enumerate(line_splitted):
            line_splitted[ls_i] = sentence_padding(sentence=ls, max_length=sequence_length)
        # 向后补齐num_sentences
        pad_num = num_sentences - len(line_splitted)
        if pad_num < 0:
            line_splitted = line_splitted[-1*num_sentences:]
        while pad_num > 0:
            line_splitted.append([1 for _ in range(sequence_length)])  # <PAD>
            pad_num -= 1
        dataset.append(line_splitted)
    print(np.shape(dataset))
    # [total_size, num_sentences, sequence_length]
    return np.array(dataset, dtype=np.int64)

def sentence_padding(sentence, max_length):
    if len(sentence) <= max_length:
        for _ in range(max_length-len(sentence)):
            sentence.append(1)
    else:
        sentence = sentence[max_length*(-1):]
    return sentence

def sentences_splitted(text, split_chars=["。"]):
    # text : list, 1-dim
    # 按照分隔符进行分句
    splitted = []
    idxs = [i for i, a in enumerate(text) if a in split_chars]
    for i, _ in enumerate(idxs):
        if i == 0:
            splitted.append(text[:idxs[i] + 1])
        else:
            splitted.append(text[idxs[i - 1] + 1: idxs[i] + 1])
    return splitted
