import requests
from bs4 import BeautifulSoup
import time
import pandas as pd
import numpy as np


# Create a class to store hop data

# class Hop:



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
# print(hopLinks)

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
        cols = row.find_all(['th'])
        cols += row.find_all(['td'])
        cols = [ele.text.strip() for ele in cols]
        data.append([ele for ele in cols if ele]) # Get rid of empty values

    # return hop_name and data
    return hop_name, data


# hop dataframe to store all the data



# for each hop link, extract the data
testI = 0

# DF to store name and lenfth of data
hopData = pd.DataFrame(columns=['name', 'data_length'])

print(len(hopLinks))
for link in hopLinks:
    url = "https://beermaverick.com" + link
    hop_name, data = extractData(url)
    # print(data)
    if ["Total Oil Breakdown:"] in data:
        # print("yes")
        data.remove(["Total Oil Breakdown:"])
    print(hop_name)
    # print(len(data))
    # Add the data to the dataframe using pandas concat function
    hopData = pd.concat([hopData, pd.DataFrame([[hop_name, len(data)]], columns=['name', 'data_length'])])

    testI += 1
    if testI == 20:
        break
    # print(data)
    # add the data to the dataframe
    # seperate the min and max values


# sort the dataframe by the length of the data≠
hopData = hopData.sort_values(by=['data_length'], ascending=False)
print(hopData)