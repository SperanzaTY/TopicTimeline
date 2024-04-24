import json
import os
import re
from datetime import datetime, timedelta

import numpy as np
import pandas as pd
from collections import defaultdict
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from utils import read_csv_file, stopwordslist, seg_sentence, get_similarity
from timeline import time_line


class OutputItem:
    def __init__(self, index, text):  # 初始化
        self.index = index
        self.text = text
        self.freq = 0
        self.occurrence = []  # 出现的环境
        self.similarity = 0.0  # 相似度

    def __str__(self):  # 输出结果信息
        s = "文档序号: " + str(self.index) + \
            "\n出现频率: " + str(self.freq) + \
            "\n相关度: " + str(self.similarity) + \
            "\n语句: \n"
        for i, j in enumerate(self.occurrence):
            s += "第" + str(i + 1) + "句："
            s += "......" + self.text[max(0, j[0] - 25):j[0] + 25] + "......\n"
        return s


def process(files):
    """
    处理文件，得到词汇表、权重列表、权重矩阵和倒排索引表
    :param files:文件
    :return:
    """
    cv = CountVectorizer()  # 使用内置的英语停用词
    cv_fit = cv.fit_transform(files)
    glossary = cv.get_feature_names_out()  # 词汇表
    transformer = TfidfTransformer()
    tfidf = transformer.fit_transform(cv_fit)
    weigh_matrix = tfidf.toarray()  # 得到tf_idf的权重矩阵
    # 计算所有索引词的权重列表
    weigh_list = []
    for file in weigh_matrix:
        for j, weigh in enumerate(file):
            if weigh != 0:
                weigh_list.insert(j, weigh)
    # 计算倒排索引
    inverse_index = defaultdict(list)
    words = cv.get_feature_names_out()
    array = cv_fit.toarray()
    for i, file in enumerate(files):
        for j, word in enumerate(words):
            if array[i][j] != 0:
                position = [m.span() for m in re.finditer(
                    r'\b' + word + r'\b', file)]
                inverse_index[word].append((i, array[i][j], position))
    # print(inverse_index)
    return glossary, weigh_list, weigh_matrix, inverse_index


def generate_input_vector(input: str, glossary, weigh_list):
    """
    构建查询向量
    :param input: 用户查询列表
    :param glossary: 词汇表
    :param weigh_list: 词汇的权重列表
    :return: 查询向量
    """
    input_words = input.split()
    input_vector = []  # 初始化查询向量
    for index, word in enumerate(glossary):
        if input_words.count(word):  # 如果查询中包含词汇表里该词
            input_vector.append(weigh_list[index])
        else:
            input_vector.append(0)
    return input_vector


def search(input: str, input_vector: list, inverse_index, weigh_matrix, texts):
    """
    查找
    :param input: 用户输入
    :param input_vector: 查询向量
    :param inverse_index: 倒排索引表
    :param weigh_matrix: 文档向量（权重矩阵）
    :param texts: 文档
    :return: 查询结果
    """
    input_words = input.split(" ")
    docs_list = []
    # 利用倒排索引查询文档列表
    for input_word in input_words:
        docs_list.append(inverse_index[input_word].copy())
    result_dict = {}  # 存储结果
    for index, i in enumerate(docs_list):  # 遍历文本
        if not i:
            continue
        for j in i:  # i存放的是数据位置
            item = OutputItem(j[0], texts[j[0]])
            item.freq += j[1]
            item.occurrence.extend(j[2])
            result_dict[j[0]] = item

    result_list = [i for i in result_dict.values()]

    # 计算每个结果的相似性
    for i in result_list:
        i.similarity = get_similarity(input_vector, weigh_matrix[i.index])

    result_list.sort(key=lambda x: -x.similarity)  # 按相似性排序
    if len(result_list) > 50:
        result_list = result_list[0:50]
    return result_list


def retrival():
    print("\n**************************热搜时间轴生成系统****************************\n")
    start = input("请输入起始时间(示例: 2023-01):")
    end = input("请输入截止时间(示例: 2023-02):")
    searchs = input("请输入关键词(输入EXIT退出):")
    tittle = searchs

    start_date = datetime.strptime(start, '%Y-%m')
    end_date = datetime.strptime(end, '%Y-%m')
    current_date = start_date

    rows = []
    date = []
    mind = []
    while current_date <= end_date:
        month_str = current_date.strftime('%Y-%m')
        file_path = os.path.join('topic/', f'{month_str}_new.csv')
        # print(file_path)
        try:
            # 读取CSV文件内容
            time, row, mind = read_csv_file(file_path)
            rows.extend(row)
            date.extend(time)
            mind.extend(mind)
            print(f'Read data for {month_str}')
        except FileNotFoundError:
            print(f'File {file_path} not found.')

        current_date = current_date + timedelta(days=32)
        current_date = current_date.replace(day=1)  # 将日期设置为下一个月的第一天

    # csv_file_path = 'AG_topic.csv'
    # rows = read_csv_file(csv_file_path)

    jieba_seg = []
    for line in rows:
        line_seg = seg_sentence(line)  # 这里的返回值是字符串
        # outputs.write(line_seg + '\n')
        jieba_seg.append(line_seg)

    glossary, weigh_list, weigh_matrix, inverse_index = process(jieba_seg)

    while searchs != "EXIT":
        index_list = []
        topic_list = []
        date_list = []
        mind_list = []
        row_list = []

        vec = generate_input_vector(searchs, glossary, weigh_list)
        results = search(searchs, vec, inverse_index, weigh_matrix, jieba_seg)
        if len(results) == 0:
            print("抱歉，未找到相关结果。\n")
        else:
            for i, result in enumerate(results):
                print("****************************第", i + 1, "条结果*******************************\n", result)
                index_list.append(result.index)



        for i in index_list:
            topic_list.append(rows[i].split(" ")[0])
            date_list.append(date[i])
            mind_list.append(mind[i])
            row_list.append(rows[i].split(" ")[1])

        df_excel = pd.DataFrame({
            'Topic': topic_list,
            'Row': row_list,
            'Date': date_list,
            'Mind': mind_list
        })

        print(date_list[0:20])
        print(topic_list[0:20])
        print(mind_list[0:20])

        excel_name = f"result_excel/{tittle}.xlsx"

        time_line(topic_list, date_list, tittle)

        df_excel.to_excel(excel_name, index=False)

        searchs = input("请输入关键词(输入EXIT退出):")
        tittle = searchs


    print("*******************************已退出**********************************\n")


if __name__ == '__main__':
    retrival()
