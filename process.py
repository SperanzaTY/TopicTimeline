import json
import os
import boto3
import numpy as np
from datetime import datetime, timedelta
from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer
from collections import defaultdict
import re
from utils import read_csv_file, seg_sentence 

# 确定遍历的月份范围
start_month = '2022-11'
end_month = '2022-11'
start_date = datetime.strptime(start_month, '%Y-%m')
end_date = datetime.strptime(end_month, '%Y-%m')

# 初始化 S3 客户端
s3_client = boto3.client('s3')
bucket_name = 'topictimelinebucket'  # 替换为你的S3桶名称

def upload_to_s3(bucket, key, data):
    # 如果数据是NumPy数组，转换为列表
    if isinstance(data, np.ndarray):
        data = data.tolist()
    s3_client.put_object(Body=json.dumps(data), Bucket=bucket, Key=key)


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

# 生成所有时间段组合的函数
def generate_time_segments(start_date, end_date):
    segments = []
    while start_date <= end_date:
        month_str = start_date.strftime('%Y-%m')
        segments.append(month_str)
        start_date += timedelta(days=32)
        start_date = start_date.replace(day=1)
    return segments

# 主处理逻辑
def main():
    time_segments = generate_time_segments(start_date, end_date)
    for i in range(len(time_segments)):
        for j in range(i, len(time_segments)):
            start_segment = time_segments[i]
            end_segment = time_segments[j]
            print(start_segment+" to "+end_segment+" genertating ...")

            rows, date, mind = [], [], []
            current_date = datetime.strptime(start_segment, '%Y-%m')

            while current_date.strftime('%Y-%m') <= end_segment:
                month_str = current_date.strftime('%Y-%m')
                file_path = os.path.join('topic/', f'{month_str}_new.csv')
                try:
                    time, row, mind_data = read_csv_file(file_path)
                    rows.extend(row)
                    date.extend(time)
                    mind.extend(mind_data)
                except FileNotFoundError:
                    print(f'File {file_path} not found.')
                current_date += timedelta(days=32)
                current_date = current_date.replace(day=1)

            jieba_seg = [seg_sentence(line) for line in rows]
            glossary, weigh_list, weigh_matrix, inverse_index = process(jieba_seg)

            # 上传到S3
            upload_to_s3(bucket_name, f'{start_segment}_{end_segment}_glossary.json', glossary)
            upload_to_s3(bucket_name, f'{start_segment}_{end_segment}_weigh_matrix.json', weigh_matrix)
            upload_to_s3(bucket_name, f'{start_segment}_{end_segment}_inverse_index.json', inverse_index)
            print("upload "+start_segment+" to "+end_segment+" success！")

if __name__ == "__main__":
    main()
