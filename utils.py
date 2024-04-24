import csv
import math
import time
import jieba


def read_csv_file(file_path):
    rows = []
    date = []
    mind = []

    with open(file_path, 'r', encoding='utf-8') as file:
        csv_reader = csv.reader(file)
        for i, row in enumerate(csv_reader):
            if i != 0:  # Skip header row
                row_length = len(row)
                if row_length >= 5:
                    five_element = row[4]  # Fourth element of the row
                    six_element = row[5]

                    # Find the index of the last comma in the fourth element
                    index_last_comma = five_element.rfind(',')

                    # Combine third element and appropriate part of fourth element
                    combined_string = five_element + " " + six_element[3:index_last_comma]  # Adjust as needed
                    date.append(row[3])
                    rows.append(combined_string)
                    mind.append(row[6])
    return date, rows, mind


def stopwordslist(filepath):
    stopwords = [line.strip() for line in open(filepath, 'r', encoding='utf-8').readlines()]
    return stopwords


def seg_sentence(text):
    # 中文分词
    sentence_seged = jieba.lcut(text.strip())
    stopwords = stopwordslist('stopwords.txt')  # 这里加载停用词的路径
    outstr = ''
    for word in sentence_seged:
        if word not in stopwords:
            if word != '\t':
                outstr += word
                outstr += " "
    return outstr


def get_similarity(a, b):
    """
    计算两个向量的相似度（余弦夹角）
    :param a: 向量a
    :param b: 向量b
    :return: 相似度
    """
    dot = 0
    len_a = 0
    len_b = 0
    for i in range(len(a)):
        dot += a[i] * b[i]
        len_a += a[i] * a[i]
        len_b += b[i] * b[i]
    len_a = math.sqrt(len_a)
    len_b = math.sqrt(len_b)
    return dot / (len_a * len_b)
