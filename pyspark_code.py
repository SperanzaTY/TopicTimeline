import os
os.environ['PYSPARK_PYTHON'] = '/Users/lyu/anaconda3/envs/spark/bin/python' #your spark pathway

import time
from pyspark import SparkConf, SparkContext
from pyspark.sql import SparkSession
from pyspark.ml.feature import IDF, CountVectorizer, Tokenizer
from pyspark.sql.functions import udf, concat_ws
from pyspark.sql.types import StringType, ArrayType
from utils import read_csv_file, stopwordslist, seg_sentence, get_similarity
from collections import defaultdict
import os
import json
import re
from datetime import datetime, timedelta
import numpy as np
from dateutil.relativedelta import relativedelta
from pyspark.sql.functions import when

sparkConf = SparkConf().setAppName("TextSearch")
sc = SparkContext(conf=sparkConf)
spark = SparkSession(sc)

seg_sentence_udf = udf(seg_sentence, ArrayType(StringType()))
cv = CountVectorizer(inputCol="words", outputCol="raw_features")
idf = IDF(inputCol="raw_features", outputCol="features")

# Define start and end times
start_date = datetime.strptime('2022-11', '%Y-%m')
end_date = datetime.strptime('2023-10', '%Y-%m')
original_start_date = start_date
current_date = start_date

# Define DataFrame
df_main = None

while current_date <= end_date:
    month_str = current_date.strftime('%Y-%m')
    file_path = os.path.join('topic/', f'{month_str}_new.csv')
    try:
        start_time = time.time()
        # Read CSV file into DataFrame
        df = spark.read.csv(file_path, header=True)

        df = df.withColumn('Title', when(df['Title'].isNull(), '').otherwise(df['Title']))
        df = df.withColumn('Introduction', when(df['Introduction'].isNull(), '').otherwise(df['Introduction']))

        # Combine 'Title' and 'Introduction' into a single column
        df = df.withColumn('text', concat_ws(' ', df['Title'], df['Introduction']))

        # Use UDF to perform word segmentation
        df = df.na.fill({'text': ''})  # fill null values with empty string
        df = df.withColumn("words", seg_sentence_udf(df['text']))

        # Use CountVectorizer and IDF to transform text into TF-IDF
        cv_model = cv.fit(df)
        df = cv_model.transform(df)
        idf_model = idf.fit(df)
        df = idf_model.transform(df)

        # Merge df into df_main
        if df_main:
            df_main = df_main.union(df)
        else:
            df_main = df

        print(f"Processed data for {month_str}")
        end_time = time.time()
        print(f"Time elapsed: {end_time - start_time}")
        print(" ")

    except FileNotFoundError:
        print(f"File {file_path} not found.")

        # Increment current_date to next month
    current_date += relativedelta(months=1)

df_main.show()
