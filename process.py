import json
import os
import io
import pickle
import boto3
import numpy as np
from datetime import datetime, timedelta
from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer
from collections import defaultdict
import re
from utils import read_csv_file, seg_sentence 
import numpy as np
import json
import os
from collections import defaultdict

# 确定遍历的月份范围
start_month = '2022-11'
end_month = '2023-10'
start_date = datetime.strptime(start_month, '%Y-%m')
end_date = datetime.strptime(end_month, '%Y-%m')
local_directory = '/home/ubuntu/vec'

def save_with_pickle(data, directory, filename):
    """使用pickle将数据保存到本地文件系统"""
    # 确保目录存在
    if not os.path.exists(directory):
        os.makedirs(directory)
    # 文件的完整路径
    filepath = os.path.join(directory, filename)
    # 使用pickle保存数据
    with open(filepath, 'wb') as f:  # 'wb' 表示二进制写模式
        pickle.dump(data, f)

# 初始化 S3 客户端
s3_client = boto3.client('s3')
bucket_name = 'topictimelinebucket'  # 替换为你的S3桶名称

def upload_to_s3(data, bucket_name, key):
    """使用pickle将数据直接保存到S3"""
    # 序列化数据
    buffer = io.BytesIO()
    pickle.dump(data, buffer)
    buffer.seek(0)
    
    # 初始化S3客户端并上传数据
    s3_client = boto3.client('s3')
    s3_client.upload_fileobj(buffer, bucket_name, key)
    print(f"Uploaded {key} to S3")

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

            jieba_seg = []
            for line in rows:
                line_seg = seg_sentence(line)  # 这里的返回值是字符串
                # outputs.write(line_seg + '\n')
                jieba_seg.append(line_seg)

            glossary, weigh_list, weigh_matrix, inverse_index = process(jieba_seg)

            # 上传到S3
            save_directory = f'{start_segment}_{end_segment}'

            print(f"Data for {start_segment} to {end_segment} glossary saving to S3...")
            upload_to_s3(glossary, bucket_name, f'{save_directory}/{start_segment}_{end_segment}_glossary.pkl')
            print(f"Data for {start_segment} to {end_segment} weigh list saving to S3...")
            upload_to_s3(weigh_list, bucket_name, f'{save_directory}/{start_segment}_{end_segment}_weigh_list.pkl')
            print(f"Data for {start_segment} to {end_segment} weigh matrix saving to S3...")
            upload_to_s3(weigh_matrix, bucket_name, f'{save_directory}/{start_segment}_{end_segment}_weigh_matrix.pkl')
            print(f"Data for {start_segment} to {end_segment} inverse index saving to S3...")
            upload_to_s3(inverse_index, bucket_name, f'{save_directory}/{start_segment}_{end_segment}_inverse_index.pkl')
            print(f"Data for {start_segment} to {end_segment} jieba_seg saving to S3...")
            upload_to_s3(jieba_seg, bucket_name, f'{save_directory}/{start_segment}_{end_segment}_jieba_seg.pkl')

            print(f"Data for {start_segment} to {end_segment} saved to S3.")

            # # 保存到本地
            # save_directory = f'{local_directory}/{start_segment}_{end_segment}'
            # print(f"Data for {start_segment} to {end_segment} glossary saving locally...")
            # save_with_pickle(glossary, save_directory, f'{start_segment}_{end_segment}_glossary.pkl')
            # print(f"Data for {start_segment} to {end_segment} weigh list saving locally...")
            # save_with_pickle(weigh_list, save_directory, f'{start_segment}_{end_segment}_weigh_list.pkl')
            # print(f"Data for {start_segment} to {end_segment} weigh matrix saving locally...")
            # save_with_pickle(weigh_matrix, save_directory, f'{start_segment}_{end_segment}_weigh_matrix.pkl')
            # print(f"Data for {start_segment} to {end_segment} inverse index saved locally...")
            # save_with_pickle(inverse_index, save_directory, f'{start_segment}_{end_segment}_inverse_index.pkl')
            # print(f"Data for {start_segment} to {end_segment} jieba_seg saved locally...")
            # save_with_pickle(jieba_seg, save_directory, f'{start_segment}_{end_segment}_jieba_seg.pkl')
            # print(f"Data for {start_segment} to {end_segment} saved locally.")

if __name__ == "__main__":
    main()
