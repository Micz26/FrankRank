from bs4 import BeautifulSoup
import requests
import random
import regex as re
import pandas as pd
import json

class Yahoo:
    def __init__(self, url : str = ''):
        self.url = url
        self.headers_list = [
                        'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36',
                        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36'
                        "Mozilla/5.0 (Windows NT 10.0; rv:91.0) Gecko/20100101 Firefox/91.0",
                        "Mozilla/5.0 (Windows NT 10.0; rv:78.0) Gecko/20100101 Firefox/78.0",
                        "Mozilla/5.0 (X11; Linux x86_64; rv:95.0) Gecko/20100101 Firefox/95.0",
                        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.1.1 Safari/605.1.15',
                        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:77.0) Gecko/20100101 Firefox/77.0',
                        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36',
                        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:77.0) Gecko/20100101 Firefox/77.0',
                        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36'
                        ] 
        self.soup = ""
        self.headers = {'User-Agent' : random.choice(self.headers_list) }

    def get_soup(self):
        r = requests.get(self.url, headers = self.headers, timeout=1000)
        self.soup = BeautifulSoup(r.content, "lxml")
        
        return self.soup
    
    def get_soupTextYahoo(self):
        if not self.soup:
            soup = self.get_soup()
        
        soupText = soup.find_all("div", {"class":"caas-body"})[0]
        
        return str(soupText.text)

class NBP(Yahoo):
    def __init__(self, url : str = 'https://www.obligacjeskarbowe.pl/'):
        super().__init__(url) 
        self.soup = ""
        self.offertListLinks = []
        
    def make_offertListLinks(self):
        if not self.soup:
            soup = self.get_soup()
        
        classSoup = soup.find_all("div", {"class":"product-card"})
        for item in classSoup[:-1]:
            revenue_symbol = re.compile('(?<=href=")(.*?)(?=">)')
            link = re.findall(revenue_symbol, str(item))[0]
            link = f"https://www.obligacjeskarbowe.pl/{link}"
            self.offertListLinks.append(link)
        
        return self.offertListLinks
    
    def get_bondOffer(self, link):
        self.url = link
        soup = self.get_soup()
        labels = soup.find_all("strong", {"class":"product-details__list-label"})
        values = soup.find_all("span", {"class":"product-details__list-value"})
        
        offer = {}
        for i in range(len(labels)):
            valuePattern = '(?<=>\n                                    )(.*?)(?=\n)'
            val = re.findall(valuePattern, str(values[i]))[0]
            valNoSpace = val.replace(" ", "")
            if not val or not valNoSpace:
                val = str(values[i].text)
                val = val.replace("\n", "")
                val = val.split()
                val = ' '.join([str(elem) for elem in val])
                val = val.replace(" Zobacz tabelę odsetkową", "")
            
            label = str(labels[i].text).split()
            label = ' '.join([str(elem) for elem in label])
            label = label.replace(":","")
            
            offer[label] = val                
        return offer
        
    def get_nbpBondsdictList(self):
        if not self.offertListLinks:
            self.offertListLinks = self.make_offertListLinks()
        
        dictList = []
        for link in self.offertListLinks:
            dictList.append(self.get_bondOffer(link))
        
        return dictList
    
    def get_nbpBondsDataframe(self):
        """ Scrapes bond info from https://www.obligacjeskarbowe.pl/
        
            Returns :
                df : Columns - ['Seria', 'Oprocentowanie', 'Kapitalizacja odsetek', 'Wypłata odsetek',
                      'Okres oprocentowania', 'Sprzedaż', 'Cena sprzedaży jednej obligacji',
                      'Cena zamiany jednej obligacji', 'Odsetki']
        """
        dictList = self.get_nbpBondsdictList()
        df = pd.DataFrame(dictList)
        return df
        
    def get_nbpBondsJSON(self):
        """ Scrapes bond info from https://www.obligacjeskarbowe.pl/
        
            Returns :
                nbpJson : Columns - ['Seria', 'Oprocentowanie', 'Kapitalizacja odsetek', 'Wypłata odsetek',
                    'Okres oprocentowania', 'Sprzedaż', 'Cena sprzedaży jednej obligacji',
                    'Cena zamiany jednej obligacji', 'Odsetki']
        """
        dictList = self.get_nbpBondsdictList()
        nbpJson = json.dumps(dictList)
        return nbpJson