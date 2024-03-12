import requests
from bs4 import BeautifulSoup as bs

file = open("webpage_content.txt", "r+", encoding = "utf-8")
file.truncate(0)

url = input("Wep page link: ")
response = requests.get(url)
content = response.text

soup = bs(content, "html.parser")
for script in soup(["script", "style"]):
    script.extract()
for text in soup.find_all(string = True):
    file.write(text)

file.close()