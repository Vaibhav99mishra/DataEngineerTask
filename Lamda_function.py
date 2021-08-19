# -*- coding: utf-8 -*-
"""
Created on Thu Aug 19 15:04:16 2021

@author: Vaibhav
"""

import json
import boto3
import csv
from io import StringIO  # python3 (or BytesIO for python2)
import boto3
import datetime
def lambda_handler (event, context):
    s3=boto3.resource('s3')
    #print("[INFO] Request COVID-19 News Related data...")
    data_scraped = start_scraping()
    BUCKET_NAME = "news_dataset"
    TimeNow= datetime.datetime.now()
    DATE= str(TimeNow)
    OUTPUT_NAME="datakey"+DATE+".json"
    OUTPUT_BODY= json.dumps(data_scraped)
    s3.Bucket(BUCKET_NAME).put_object(key=OUTPUT_NAME, Body=OUTPUT_BODY)
    #print(f "[INFO] Saving Data to s3 {BUCKET_NAME} Bucket...")
    df=json_to_df(s3)
    csv_buffer = StringIO()
    df.to_csv(csv_buffer)
    #s3.Bucket(BUCKET_NAME).put_object(, Body=OUTPUT_BODY)
    s3.Object(BUCKET_NAME, 'df.csv').put(Body=csv_buffer.getvalue())
    #print(f"[INFO] Job done at (DATE)")