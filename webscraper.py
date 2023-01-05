import requests
from bs4 import BeautifulSoup
import time
import pandas as pd
import numpy as np


hopListURL = "https://beermaverick.com/hops/"

page = requests.get(hopListURL)
soup = BeautifulSoup(page.content, 'html.parser')
results = soup.find(id='content')

# Get all the hop links
hopLinks = []
for link in results.find_all('a'):
    hopLinks.append(link.get('href'))

# filter out the links that are not hops
hopLinks = [x for x in hopLinks if "/hop/" in x]
print(hopLinks)

# "https://beermaverick.com/hop/brooklyn/"

def extractData(url):
    page = requests.get(url)

    soup = BeautifulSoup(page.content, 'html.parser')

    results = soup.find(id='content')

    hop_name = results.find('h1', class_='entry-title').text

    data = []
    table = soup.find('table', attrs={'class':'brewvalues'})

    rows = table.find_all('tr')
    for row in rows:
        cols = row.find_all('td')
        cols = [ele.text.strip() for ele in cols]
        data.append([ele for ele in cols if ele]) # Get rid of empty values

    # return hop_name and data
    return hop_name, data


# hop dataframe to store all the data
hop_df = pd.DataFrame(columns=['hop_name', 'alpha_acid', 'beta_acid', 'cohumulone', 'total_oil', 'myrcene', 'humulene', 'caryophyllene', 'farnesene', 'geraniol', 'linalool', 'alpha_acid_min', 'alpha_acid_max', 'beta_acid_min', 'beta_acid_max', 'cohumulone_min', 'cohumulone_max', 'total_oil_min', 'total_oil_max', 'myrcene_min', 'myrcene_max', 'humulene_min', 'humulene_max', 'caryophyllene_min', 'caryophyllene_max', 'farnesene_min', 'farnesene_max', 'geraniol_min', 'geraniol_max', 'linalool_min', 'linalool_max'])



# for each hop link, extract the data
print(len(hopLinks))
for link in hopLinks:
    url = "https://beermaverick.com" + link
    hop_name, data = extractData(url)
    print(hop_name)ß
    # print(data)
    # add the data to the dataframe
    # seperate the min and max values

    hop_df = hop_df.append({'hop_name': hop_name, 'alpha_acid': data[0][1], 'beta_acid': data[1][1], 'cohumulone': data[2][1], 'total_oil': data[3][1], 'myrcene': data[4][1], 'humulene': data[5][1], 'caryophyllene': data[6][1], 'farnesene': data[7][1], 'geraniol': data[8][1], 'linalool': data[9][1], 'alpha_acid_min': data[0][2], 'alpha_acid_max': data[0][3], 'beta_acid_min': data[1][2], 'beta_acid_max': data[1][3], 'cohumulone_min': data[2][2], 'cohumulone_max': data[2][3], 'total_oil_min': data[3][2], 'total_oil_max': data[3][3], 'myrcene_min': data[4][2], 'myrcene_max': data[4][3], 'humulene_min': data[5][2], 'humulene_max': data[5][3], 'caryophyllene_min': data[6][2], 'caryophyllene_max': data[6][3], 'farnesene_min': data[7][2], 'farnesene_max': data[7][3], 'geraniol_min': data[8][2], 'geraniol_max': data[8][3], 'linalool_min': data[9][2], 'linalool_max': data[9][3]}, ignore_index=True)