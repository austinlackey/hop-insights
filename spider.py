import requests
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
import re
import ast

baseURL = 'https://www.beermaverick.com/'

def scrape(testHops: int = -1):
    page = requests.get(baseURL + 'hops/')
    soup = BeautifulSoup(page.content, 'html.parser')
    # find wp-block-table div class and get links
    hopTable = soup.find('div', class_='wp-block-table').find_all('a')
    hopLinks = [hop['href'] for hop in hopTable]
    
    i = 0
    for hopLink in hopLinks:
        if i == testHops:
            break
        i += 1
        page = requests.get(baseURL + hopLink)
        soup = BeautifulSoup(page.content, 'html.parser')

        # Dictionary to store hop characteristics
        hopDict = {}
        # Hop Name
        hopName = soup.find('h1', class_='entry-title').text
        hopDict['Name'] = hopName

        # Hop Characteristics
        hopChar = soup.find('figure', class_='wp-block-table').find('table')
        hopChar = [char.text for char in hopChar.find_all(['th', 'td'])]
        hopChar = np.reshape(hopChar, (-1, 2))
        hopChar = pd.DataFrame(hopChar, columns=['Characteristic', 'Value'])
        hopChar['Characteristic'] = hopChar['Characteristic'].str.replace(':', '')
        hopChar = hopChar[~hopChar['Characteristic'].str.contains('Comparison')]
        hopChar = hopChar.set_index('Characteristic').T
        hopChar = hopChar.to_dict('records')[0]
        hopDict.update(hopChar)

        # Flavor Tags
        hopTags = soup.find('b', string='Tags:').find_next('em').find_all('a')
        hopTags = [tag.text for tag in hopTags]
        hopTags = [re.sub('#', '', tag) for tag in hopTags]
        hopDict['Flavor Tags'] = hopTags

        print(hopDict)

        # Aroma Profile
        aromaProfile = soup.find_all('script')
        aromaProfile = ''.join([aroma.text for aroma in aromaProfile])
        aromaProfile_start = aromaProfile.find('aromaChart')
        aromaProfile_end = aromaProfile.find('pointBackgroundColor')
        aromaProfile = aromaProfile[aromaProfile_start:aromaProfile_end]
        
        labels_start = aromaProfile.find('labels: [')
        labels_end = aromaProfile[labels_start:].find(']')
        labels = aromaProfile[labels_start+9:labels_start+labels_end]
        labels = labels.replace("'", '')
        labels = labels.split(',')
        labels = [label.strip() for label in labels]

        data_start = aromaProfile.find('data: [')
        data_end = aromaProfile[data_start:].find(']')
        data = aromaProfile[data_start+7:data_start+data_end]
        data = data.split(',')
        data = [float(datum) for datum in data]
        aromaProfile = dict(zip(labels, data))
        
        hopDict['Aroma Profile'] = aromaProfile

        print(hopDict)

scrape(testHops=1)