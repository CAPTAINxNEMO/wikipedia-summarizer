import requests
from bs4 import BeautifulSoup as bs
# import re
# import nltk

def webParser():
    # url = input("Wep page link: ")
    url = "https://en.wikipedia.org/wiki/Severe_acute_respiratory_syndrome_coronavirus_2"
    response = requests.get(url)

    soup = bs(response.content, "html.parser")
    for script in soup(["script", "style"]):
        script.extract()
    for text in soup.find_all(string = True):
        print(text)

def summarizer():
    print("Placeholder")

if __name__ == "__main__":
    webParser()
    summarizer()