import requests
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
import re
import ast

baseURL = 'https://www.beermaverick.com/'

def scrape(testHopsStart: int = -1, testHopsEnd: int = -1):
    page = requests.get(baseURL + 'hops/')
    soup = BeautifulSoup(page.content, 'html.parser')
    # find wp-block-table div class and get links
    hopTable = soup.find('div', class_='wp-block-table').find_all('a')
    hopLinks = [hop['href'] for hop in hopTable]
    
    i = 0
    if testHopsStart == -1:
        testHopsStart = 0
    if testHopsEnd == -1:
        testHopsEnd = len(hopLinks)
    hopLinks = hopLinks[testHopsStart:testHopsEnd]
    df = []
    for hopLink in hopLinks:
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
        hopTags = soup.find('b', string='Tags:')
        if hopTags is not None:
            hopTags = hopTags.find_next('em').find_all('a')
            hopTags = [tag.text for tag in hopTags]
            hopTags = [re.sub('#', '', tag) for tag in hopTags]
        hopDict['Flavor Tags'] = hopTags

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
        if data[0] == '':
            aromaProfile = None
        else:
            data = [float(datum) for datum in data]
            aromaProfile = dict(zip(labels, data))
        
        hopDict['Aroma Profile'] = aromaProfile

        # Brewing Values
        brewingTitles = soup.find('table', class_='brewvalues').find_all('th')
        brewingValues = soup.find('table', class_='brewvalues').find_all('td')
        brewingTitles = [title.text for title in brewingTitles]
        brewingValues = [value.text for value in brewingValues]
        brewingValues = [value for value in brewingValues if value != 'Total Oil Breakdown:']
        brewingTitles = [cleanTitles(title) for title in brewingTitles]
        removeStr = ['(%)', '(mL/100g)']
        for string in removeStr:
            brewingTitles = [value.replace(string, '').strip() for value in brewingTitles]
        brewingValues = [cleanValues(value) for value in brewingValues]
        # for each title, if the length of the value array is 3, create a new title with the same name and append 'Low', 'High', 'High', if the length is 2, append 'Low', 'High'
        for i in range(len(brewingTitles)):
            if brewingValues[i] is None:
                hopDict[brewingTitles[i]] = None
                continue
            if brewingValues[i] == 'Unknown':
                hopDict[brewingTitles[i]] = 'Unknown'
                continue
            if len(brewingValues[i]) >= 2:
                hopDict[brewingTitles[i] + ' Low'] = brewingValues[i][0]
                hopDict[brewingTitles[i] + ' High'] = brewingValues[i][1]
            if len(brewingValues[i]) == 3:
                hopDict[brewingTitles[i] + ' Avg'] = brewingValues[i][2]
        df.append(hopDict)
        print(hopName)
    df = pd.DataFrame(df)
    df.to_csv('hops.csv', index=False)
def cleanValues(value: str):
    if value == 'Unknown':
        return "Unknown"
    # If value is ratio
    if value.__contains__(':'):
        value = value.split(':1')
        value = [val.replace('-', '').replace('avg', '').strip() for val in value]
        value = [float(val) for val in value if val]
    else:
        value = value.replace('%', '-').replace('mL', '-').split('-')
        value = [re.sub(r'\([^)]*\)', '', val) for val in value]
        value = [val.replace('avg', '').replace('avg.', '').strip() for val in value]
        value = [val for val in value if val != '.']
        value = [float(val) for val in value if val]
    return value
        
def cleanTitles(title: str):
    if title.__contains__('Alpha Acid'):
        return 'Alpha Acid (%)'
    elif title.__contains__('Beta Acid'):
        return 'Beta Acid (%)'
    elif title.__contains__('Alpha-Beta Ratio'):
        return 'Alpha-Beta Ratio'
    elif title.__contains__('Hop Storage Index'):
        return 'Hop Storage Index'
    elif title.__contains__('Co-Humulone'):
        return 'Co-Humulone (%)'
    elif title.__contains__('Total Oils'):
        return 'Total Oils (mL/100g)'
    elif title.__contains__('MyrceneFlavors'):
        return 'Myrcene (%)'
    elif title.__contains__('HumuleneFlavors'):
        return 'Humulene (%)'
    elif title.__contains__('CaryophylleneFlavors'):
        return 'Caryophyllene (%)'
    elif title.__contains__('FarneseneFlavors'):
        return 'Farnesene (%)'
    elif title.__contains__('All Others'):
        return 'All Others (%)'
scrape(testHopsStart=-1, testHopsEnd=-1)