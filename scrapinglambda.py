# -*- coding: utf-8 -*-
"""
Created on Wed Aug 18 21:19:41 2021

@author: abhit
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
#import nltk
import os,json
import glob

#nltk.download('punkt')

def start_scraping():
    # Request
    url ="https://www.mirror.co.uk"
    r1 = requests.get(url)
    print(r1.status_code)
    
    # We'll save in coverpage the cover page content
    coverpage = r1.content
    
    # Soup creation
    soup1 = BeautifulSoup(coverpage, 'html5lib')
    
    # News identification
    coverpage_news = soup1.find_all('article', class_='story story--news')
    #len(coverpage_news)
    
    n=1
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
    number_of_articles = 200
    # Empty lists for content, links and titles
    
    for n in np.arange(0, number_of_articles):
        # Getting the link of the article
        link = coverpage_news[n].find('a')['href']
        # Getting the title
        title = coverpage_news[n].find('h2').get_text()
        # Reading the content (it is divided in paragraphs)
        article = requests.get(link,headers=headers)
        article_content = article.content
        soup_article = BeautifulSoup(article_content, 'html5lib')
        x = soup_article.find_all('p')
        
        # Unifying the paragraphs
        list_paragraphs = []
        for p in range(0, len(x)+1):
            paragraph = x[p].get_text()
            list_paragraphs.append(paragraph)
            final_article = " ".join(list_paragraphs)
            
        stop_words=['covid','coronavirus']
    
        some_text=final_article
        #lowered = some_text.lower()
        tokens = some_text.split(' ')
        keywords = [keyword for keyword in tokens if keyword.isalpha() and keyword in stop_words]
        keywords_string = ','.join(keywords)
        return {
            'Title':title,
            'Link':link,
            'Content':final_article,
            'Keywords_Extracted':keywords_string
            }

def json_to_df(json_path):
    df = pd.DataFrame()
    path_to_json = json_path 
    json_pattern = os.path.join(path_to_json,'*.json')
    file_list = glob.glob(json_pattern)
    for file in file_list:
        data = pd.read_json(file, lines=True)
        df = df.append(data)
    return df
