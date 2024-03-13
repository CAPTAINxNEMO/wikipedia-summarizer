import requests
import wikipediaapi
from bs4 import BeautifulSoup as bs
# import re
# import nltk

# url = input("Wep page link: ")
url = "https://en.wikipedia.org/wiki/Severe_acute_respiratory_syndrome_coronavirus_2"
response = requests.get(url)

soup = bs(response.content, "html.parser")
content_div = soup.find("div", id = "bodyContent")
paragraphs = content_div.find_all("p")

text = ""
for p in paragraphs:
    text += p.get_text() + "\n"
print(text)