import re

import pandas as pd
import requests
from bs4 import BeautifulSoup
from time import sleep, time
import os
import json
"""
def getReviewPage(url=''):
    for possibleUrl in (url, url + '/1/'):  # super-8 review had a an extra /1/ on the end
        soup = BeautifulSoup(requests.get(possibleUrl).text, 'html.parser')
        reviewDivHtmlStr = str(soup.find("div", {'class': "review body-text -prose -hero -loose"}))
        sleep(.05)
        if not reviewDivHtmlStr == 'None':
            my_string = '<p>' + reviewDivHtmlStr.split('<div><p>')[-1].replace('</div>', '')
            print(my_string)
            return re.sub(r'<(\/?p|br).*?>', ' ', my_string)
            

print(getReviewPage("https://letterboxd.com/redlettermedia/film/drive-angry/"))
"""

directory = "C:\\Users\Connor\Desktop\\370\letterboxdCorpus"

dfs = []
for filename in os.listdir(directory):
        if filename.endswith('.json'):
            file_path = os.path.join(directory, filename)
            with open(file_path, 'r') as file:
                data = json.load(file)
                userDf = pd.DataFrame.from_dict(data)
                dfs.append(userDf)
df = pd.concat(dfs, ignore_index=False)
print(df)
df.to_csv("C:/Users/Connor/Desktop/370/letterboxdCorpus/all2.csv")