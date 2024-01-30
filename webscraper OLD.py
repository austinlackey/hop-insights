import requests
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
import re

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

# "https://beermaverick.com/hop/brooklyn/"

# Function to extract the data from the hop page
def extractData(url):
    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'html.parser')
    results = soup.find(id='content')
    hop_name = results.find('h1', class_='entry-title').text

    data = []
    for hit in soup.findAll(attrs={'class' : 'brewvalues'}):
        data = (hit.get_text("@--**--@").replace("\n", "").split("@--**--@"))
    
    data = list(filter(None, data)) # get rid of the empty strings
    return hop_name, data

# List of the names of the acids for reference
acidNames = ["Alpha Acid % (AA)", "Beta Acid %", "Alpha-Beta Ratio", "Hop Storage Index (HSI)", 
    "Co-Humulone as % of Alpha", "Total Oils (mL/100g)", "›\xa0 Myrcene", "›\xa0 Humulene", "›\xa0 Caryophyllene", "›\xa0 Farnesene", "›\xa0 All Others"]

# List of the acid data that can be used for dataframe names
reducedAcidNames = ["alpha_acid_min", "alpha_acid_max", "alpha_acid_avg", 
    "beta_acid_min", "beta_acid_max", "beta_acid_avg", 
    "alpha_beta_ratio_min_first", "alpha_beta_ratio_min_second", "alpha_beta_ratio_max_first", "alpha_beta_ratio_max_second", "alpha_beta_ratio_avg_first", "alpha_beta_ratio_avg_second",
    "hsi_min", "hsi_max", "hsi_avg", 
    "cohumulone_min", "cohumulone_max", "cohumulone_avg", 
    "total_oils_min", "total_oils_max", "total_oils_avg", 
    "myrcene_min", "myrcene_max", "myrcene_avg", 
    "humulene_min", "humulene_max", "humulene_avg", 
    "caryophyllene_min", "caryophyllene_max", "caryophyllene_avg", 
    "farnesene_min", "farnesene_max", "farnesene_avg", 
    "other_oils_min", "other_oils_max", "other_oils_avg"]

# Function to replace all the unneeded characters in a string
def replace_chars(string):
    listChars = ["%", " ", "avg", "mL", "(good)", "(Good)", "(Great)", "(Poor)", "(Fair)"]
    for char in listChars: # For each character in the list
        string = string.replace(char, "") # Replace the character with nothing
    return string

# Function to format the data into a nested list
def formatData(data):
    finalData = []
    for i in range(len(data)): # For each item in the data
        if data[i] in acidNames: # If the item is an acid name
            acidData = []
            acidData.append(data[i]) # Add the acid name to the list
            nextData = data[i+1] # Get the next item
            numVals = 0
            percents = [] # List to hold the values
            while(nextData not in acidNames and i < len(data) and numVals < 2): # While the next item is not an acid name and there are less than 2 values
                if re.search(r"^\d", nextData): # If the next item is a number
                    percents.append(nextData) # Add it to the list
                    numVals += 1 # Increment the number of values
                i += 1 # Increment the index
                if i < len(data):
                    nextData = data[i] # Get the next item
            acidData.append(percents) # Add the list of values to the acid data
            finalData.append(acidData) # Add the acid data to the final data

    # Formatting the data
    for i in range(len(finalData)): # For each acid
        for j in range(len(finalData[i][1])): # For each value in the acid
            # Get rid of the %, mL, and other characters
            finalData[i][1][j] = replace_chars(finalData[i][1][j])
            if "-" in finalData[i][1][j]: # If there is a dash (meaning there is a range)
                finalData[i][1][j] = finalData[i][1][j].split("-") # Split the string into a list
                if len(finalData[i][1][j]) == 2: # If there are two values
                    # Converting each value to a float

                    # First Value
                    if ":" not in finalData[i][1][j][0]: # If there is no colon (meaning there is no ratio)
                        finalData[i][1][j][0] = float(finalData[i][1][j][0]) # Convert the value to a float
                    else: # If there is a colon (meaning there is a ratio)
                        finalData[i][1][j][0] = finalData[i][1][j][0].split(":") # Split the ratio into a list
                        for k in range(len(finalData[i][1][j][0])): # For each value in the ratio
                            finalData[i][1][j][0][k] = float(finalData[i][1][j][0][k]) # Convert each value to a float
                    
                    # Second Value
                    if ":" not in finalData[i][1][j][1]: # If there is no colon (meaning there is no ratio)
                        finalData[i][1][j][1] = float(finalData[i][1][j][1]) # Convert the value to a float
                    else: # If there is a colon (meaning there is a ratio)
                        finalData[i][1][j][1] = finalData[i][1][j][1].split(":") # Split the ratio into a list
                        for k in range(len(finalData[i][1][j][1])): # For each value in the ratio
                            finalData[i][1][j][1][k] = float(finalData[i][1][j][1][k]) # Convert each value to a float
            
            elif ":" in finalData[i][1][j]: # If there is a colon (meaning there is a ratio) and no dash
                finalData[i][1][j] = finalData[i][1][j].split(":") # Split the ratio into a list
                for k in range(len(finalData[i][1][j])): # For each value in the ratio
                    finalData[i][1][j][k] = float(finalData[i][1][j][k]) # Convert each value to a float

            else: # If there is no dash or colon
                # if the string ends with an "." then remove it from the string
                if finalData[i][1][j][-1] == ".":
                    finalData[i][1][j] = finalData[i][1][j][:-1]
                finalData[i][1][j] = float(finalData[i][1][j]) # Convert the value to a float
    row = np.repeat(np.nan, len(reducedAcidNames))
    for i in range(len(finalData)):
    #     acidNames = ["Alpha Acid % (AA)", "Beta Acid %", "Alpha-Beta Ratio", "Hop Storage Index (HSI)", 
    # "Co-Humulone as % of Alpha", "Total Oils (mL/100g)", "Myrcene", "Humulene", "Caryophyllene", "Farnesene", "All Others"]
        match finalData[i][0]:
            case "Alpha Acid % (AA)":
                if len(finalData[i][1]) == 2:
                    if type(finalData[i][1][0]) == list:
                        if len(finalData[i][1][0]) == 2:
                            row[reducedAcidNames.index("alpha_acid_min")] = finalData[i][1][0][0]
                            row[reducedAcidNames.index("alpha_acid_max")] = finalData[i][1][0][1]
                        row[reducedAcidNames.index("alpha_acid_avg")] = finalData[i][1][1]
                    else:
                        row[reducedAcidNames.index("alpha_acid_avg")] = finalData[i][1][0]
            case "Beta Acid %":
                if len(finalData[i][1]) == 2:
                    if type(finalData[i][1][0]) == list:
                        if len(finalData[i][1][0]) == 2:
                            row[reducedAcidNames.index("beta_acid_min")] = finalData[i][1][0][0]
                            row[reducedAcidNames.index("beta_acid_max")] = finalData[i][1][0][1]
                        row[reducedAcidNames.index("beta_acid_avg")] = finalData[i][1][1]
                    else:
                        row[reducedAcidNames.index("beta_acid_avg")] = finalData[i][1][0]
            case "Alpha-Beta Ratio":
                if len(finalData[i][1]) == 2:
                    if len(finalData[i][1][0]) == 2:
                        row[reducedAcidNames.index("alpha_beta_ratio_min_first")] = finalData[i][1][0][0][0]
                        row[reducedAcidNames.index("alpha_beta_ratio_min_second")] = finalData[i][1][0][0][1]
                        row[reducedAcidNames.index("alpha_beta_ratio_max_first")] = finalData[i][1][0][1][0]
                        row[reducedAcidNames.index("alpha_beta_ratio_max_second")] = finalData[i][1][0][1][1]
                    row[reducedAcidNames.index("alpha_beta_ratio_avg_first")] = finalData[i][1][1][0]
                    row[reducedAcidNames.index("alpha_beta_ratio_avg_second")] = finalData[i][1][1][1]
            case "Hop Storage Index (HSI)":
                if len(finalData[i][1]) == 2:
                    if type(finalData[i][1][1]) == list:
                        row[reducedAcidNames.index("hsi_avg")] = finalData[i][1][0]
                    else:
                        row[reducedAcidNames.index("hsi_min")] = finalData[i][1][0]
                        row[reducedAcidNames.index("hsi_max")] = finalData[i][1][1]
                else:
                    row[reducedAcidNames.index("hsi_avg")] = finalData[i][1][0]
            case "Co-Humulone as % of Alpha":
                if len(finalData[i][1]) == 2:
                    if type(finalData[i][1][0]) == list:
                        if len(finalData[i][1][0]) == 2:
                            row[reducedAcidNames.index("cohumulone_min")] = finalData[i][1][0][0]
                            row[reducedAcidNames.index("cohumulone_max")] = finalData[i][1][0][1]
                        row[reducedAcidNames.index("cohumulone_avg")] = finalData[i][1][1]
                    else:
                        row[reducedAcidNames.index("cohumulone_avg")] = finalData[i][1][0]
            case "Total Oils (mL/100g)":
                # Check if the type is a list
                if len(finalData[i][1]) == 2:
                    if type(finalData[i][1][0]) == list:
                        if len(finalData[i][1][0]) == 2:
                            row[reducedAcidNames.index("total_oils_min")] = finalData[i][1][0][0]
                            row[reducedAcidNames.index("total_oils_max")] = finalData[i][1][0][1]
                        row[reducedAcidNames.index("total_oils_avg")] = finalData[i][1][1]
                    else:
                        row[reducedAcidNames.index("total_oils_avg")] = finalData[i][1][1]
            case "›\xa0 Myrcene":
                if len(finalData[i][1]) == 2:
                    if len(finalData[i][1][0]) == 2:
                        row[reducedAcidNames.index("myrcene_min")] = finalData[i][1][0][0]
                        row[reducedAcidNames.index("myrcene_max")] = finalData[i][1][0][1]
                    row[reducedAcidNames.index("myrcene_avg")] = finalData[i][1][1]
            case "›\xa0 Humulene":
                if len(finalData[i][1]) == 2:
                    if len(finalData[i][1][0]) == 2:
                        row[reducedAcidNames.index("humulene_min")] = finalData[i][1][0][0]
                        row[reducedAcidNames.index("humulene_max")] = finalData[i][1][0][1]
                    row[reducedAcidNames.index("humulene_avg")] = finalData[i][1][1]
            case "›\xa0 Caryophyllene":
                if len(finalData[i][1]) == 2:
                    if len(finalData[i][1][0]) == 2:
                        row[reducedAcidNames.index("caryophyllene_min")] = finalData[i][1][0][0]
                        row[reducedAcidNames.index("caryophyllene_max")] = finalData[i][1][0][1]
                    row[reducedAcidNames.index("caryophyllene_avg")] = finalData[i][1][1]
            case "›\xa0 Farnesene":
                if len(finalData[i][1]) == 2:
                    if len(finalData[i][1][0]) == 2:
                        row[reducedAcidNames.index("farnesene_min")] = finalData[i][1][0][0]
                        row[reducedAcidNames.index("farnesene_max")] = finalData[i][1][0][1]
                    row[reducedAcidNames.index("farnesene_avg")] = finalData[i][1][1]
            case "›\xa0 All Others":
                if len(finalData[i][1]) == 2:
                    if len(finalData[i][1][0]) == 2:
                        row[reducedAcidNames.index("other_oils_min")] = finalData[i][1][0][0]
                        row[reducedAcidNames.index("other_oils_max")] = finalData[i][1][0][1]
                    row[reducedAcidNames.index("other_oils_avg")] = finalData[i][1][1]
                else:
                    if len(finalData[i][1][0]) == 2:
                        row[reducedAcidNames.index("other_oils_min")] = finalData[i][1][0][0]
                        row[reducedAcidNames.index("other_oils_max")] = finalData[i][1][0][1]
    return row.astype(str)
    

# for each hop link, extract the data
testI = 0

df = []

print(len(hopLinks))
for link in hopLinks:
    url = "https://beermaverick.com" + link
    hop_name, data = extractData(url)
    print(hop_name)
    print("HOP #", testI + 1)
    # print(data)
    row = formatData(data)
    # append the name to the beggining of the numpy
    row = np.insert(row, 0, hop_name)
    df.append(row)
    print(row)
    print("-----")
    print()
    # testI += 1
    # if testI == 10:
    #     break
    # print(data)
    # add the data to the dataframe
    # seperate the min and max values
reducedAcidNames = np.insert(reducedAcidNames, 0 , "hop_name")
df = pd.DataFrame(df, columns=reducedAcidNames)
print(df)
df.to_csv("hop_data.csv", index=False)
# sort the dataframe by the length of the data≠