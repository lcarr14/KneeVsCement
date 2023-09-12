from urllib.request import urlopen
from bs4 import BeautifulSoup as bs
import re
from math import ceil
import numpy as np
import pandas as pd
from helper import *
from time import sleep
import ssl


def main():
    # Determine total number of pages
    context = ssl._create_unverified_context()
    set_name = input("Type set name with proper capitals and spaces: ")
    verboseness = input("Would you like ALL card information. Type 1 for yes, and 0 for no, and hit enter: ")
    output_file_name = input("What would you like your file to be called? Stick to one-word filenames: ")
    formatted_set_name = "+".join(set_name.split(" "))
    url_formatted = 'https://gatherer.wizards.com/Pages/Search/Default.aspx?page=0&set=["{}"]&sort=cn+'.format(formatted_set_name)
    print(url_formatted)
    print(type(url_formatted))
    page = urlopen(str(url_formatted), context = context) #URL HERE
    soup = bs(page, 'html.parser')
    termDisplay = soup.find("p", attrs={"class": "termdisplay"}).text.strip()
    totalCards = re.search(r'(\d+)', termDisplay).group()
    totalPages = ceil(int(totalCards) / 100)

    print("Total pages to scrape: ", totalPages)

    cardlist = []
    card_number = 0

    for pageNum in range(totalPages):
        #sleep(5)
        formatted_set_name_arg = 'https://gatherer.wizards.com/Pages/Search/Default.aspx?page={lepage}&set=["{lesetname}"]&sort=cn+'.format(lepage = pageNum, lesetname = formatted_set_name)
        page = urlopen(formatted_set_name_arg, context=context) #URL HERE
        soup = bs(page, 'html.parser')
        cardItem = soup("tr", attrs={"class": "cardItem"})

        print("Scraping page {0}/{1}".format(pageNum + 1, totalPages))

        for card in cardItem:
            #sleep()
            card_number += 1
            cardName = card.findNext("span", {"class": "cardTitle"}).text.strip()   

            cardType = card.findNext("span", {"class": "typeLine"}).text.strip()
            m = re.search(r'([\w ]+)[\s—]*([\w ]+)?[\s]*(?:\(([\d\*/]+)\))?', cardType)
            if m:
                cardType, subType, typeNum = m.group(1).strip(), m.group(2), m.group(3)         

            
            cardType, superType = getSuperType(cardType, '')

            convertedMana = card.findNext("span", {"class": "convertedManaCost"}).text.strip()

            # Get and format card rules
            rules = card.findNext("div", {"class": "rulesText"}).findAll("p")          
            rules = formatRules(rules)

            # Get abbreviated mana string
            manaCostImgs = card.findNext("span", {"class": "manaCost"}).findAll('img', alt=True)
            manaCostList = []
            for cost in manaCostImgs:
                manaCostList.append(convertSymbol(cost['alt']))
            manaCost = ''.join(manaCostList)

            # Get card set and rarity from right column
            setAndRarity = card.findNext("td", {"class": "setVersions"}).find('img', alt=True)['alt']
            cardSet, rarity = splitSetAndRarity(setAndRarity)
            if verboseness == "1":
                cardlist.append([card_number, cardName, superType, cardType, subType, typeNum, manaCost, convertedMana, cardSet, rarity, rules])
            else:
                combined_type = superType, cardType, subType
                cardlist.append([card_number, cardName, combined_type, rarity])
    columnNames = []
    if verboseness == "1":
        columnNames = ['collector#', 'cardName', 'superType', 'cardType', 'subType','typeNum', 'manaCost', 'convertedMana', 'cardSet', 'rarity', 'rules']
    else:
        columnNames = ['collector#', 'cardName', 'fullType', 'rarity']
    df = cleanUp(pd.DataFrame(cardlist, columns=columnNames), verboseness)

    df.to_csv(path_or_buf='{}.csv'.format(output_file_name), index = False)
    return

if __name__ == "__main__":
    main()