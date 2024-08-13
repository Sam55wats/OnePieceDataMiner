import json
import requests
from bs4 import BeautifulSoup
from collections import Counter
import string
import glob
import os

class Scraper:
    def __init__(self, base_url, count):
        self.base_url = base_url
        self.count = count
        self.urls = self.get_urls()
    
    def get_urls(self):
        return [f'{self.base_url}{i}' for i in range(1, self.count+1)]
    
    def get_page_content(self, url):
        page = requests.get(url).text
        return BeautifulSoup(page, 'lxml')
    
    def get_title(self, soup):
        return soup.find('h2', class_='pi-item pi-item-spacing pi-title pi-secondary-background').text
    
    def get_number(self, soup):
        return soup.find('span', class_='mw-page-title-main').text
    
    def get_short_summary(self, soup):
        return soup.find('span', id='Short_Summary').find_next('p').text
    
    def get_long_summary(self, soup):
        long_summary = ""

        long_heading = soup.find('span', id='Long_Summary')
        contents_after = long_heading.parent.find_next_siblings('p')

        for paragraph in contents_after:
            long_summary += paragraph.text

        return long_summary

    def get_characters(self):
        return []

    def scrape(self, directory):
        for url in self.urls:
            page_content = self.get_page_content(url)

            title = self.get_title(page_content)
            number = self.get_number(page_content)
            short_summary = self.get_short_summary(page_content)
            long_summary = self.get_long_summary(page_content)
            characters = self.get_characters(page_content)
            ssum_frequencies = self.get_word_frequencies(short_summary, 10)
            lsum_frequencies = self.get_word_frequencies(long_summary, 20)

            data = {
                'number': number,
                'title': title,
                'short_summary': short_summary,
                'long_summary': long_summary,
                'characters': characters,
                'ssum_frequencies': ssum_frequencies,
                'lsum_frequencies': lsum_frequencies
            }

            with open(f'{directory}/one_piece_{number}.json', 'w') as f:
                json.dump(data, f, indent = 2)

    def get_word_frequencies(self, summary, count):
        summary = summary.translate(str.maketrans('','', string.punctuation))

        split_summary = summary.split() 

        split_summary = [x.lower() for x in split_summary]

        counter = Counter(split_summary)

        frequencies = counter.most_common(count)

        return frequencies

    def character_appearances(directory):
        character_appearances = {}

        for filename in glob.glob(os.path.join(directory, '*.json')):
            with open(filename, 'r') as f:
                data = json.load(f)

                number = data['number']

                for character in data.get('characters', []):
                    if character not in character_appearances:
                        character_appearances[character] = []
                    character_appearances[character].append(number)
        
        return character_appearances