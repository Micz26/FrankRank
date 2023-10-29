from bs4 import BeautifulSoup
import requests
import random
import regex as re

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
    def __init__(self, url : str = ''):
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